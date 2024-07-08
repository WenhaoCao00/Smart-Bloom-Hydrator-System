from MQTTClient import *
from pddl_problem import *
import datetime
import subprocess
import os
from os import listdir
from os.path import isfile, join
import pathlib
from threading import Lock
import threading
import sqlite3

class DB_handler:
    def __init__(self, db_name):
        self.db_name = db_name
    
    def init(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def get_config(self):
        result = {}

        sql_cmd = """
        SELECT * FROM config;
        """
        res = self.cur.execute(sql_cmd)
        data = res.fetchone()
        key_list = ["max_temp", "min_temp", "max_mois", "min_mois", "enough_light_time", "single_water_time", "single_light_time", "trigger_period"]
        list_data = list(data)
        for i, key in enumerate(key_list):
            result[key] = list_data[i]
        
        return result
    
    def get_today_sun_data(self):
        # get database
        today_datestring = datetime.datetime.now().strftime("%d.%m.%Y")
        sql_cmd = """SELECT * FROM sunrise WHERE date = '{}';""".format(today_datestring)
        res = self.cur.execute(sql_cmd)
        result = res.fetchall()
        if len(result) > 0:
            db_data = result[0]
            return today_datestring, datetime.datetime.strptime("{} {}".format(today_datestring, db_data[1]), "%d.%m.%Y %H:%M:%S"), datetime.datetime.strptime("{} {}".format(today_datestring, db_data[2]), "%d.%m.%Y %H:%M:%S")
        else:
            return None, None, None

class AIPlanner:
    def __init__(self, sensor_topic, actuator_topic, config_topic) -> None:
        self.mqtt_client = Listener("AIPlanner")
        self.sensor_topic = sensor_topic
        self.actuator_topic = actuator_topic
        self.config_topic = config_topic

        self.pddl_pb = SmartBloomProblem()
        self.last_time_file_path = "./last_trigger_time.txt"
        self.last_trigger_time = None

        self.light_cmd_buffer_lock = Lock()
        self.light_cmd_buffer = []
        self.last_light_time = None
        self.last_light_cmd = None
        self.water_cmd_buffer_lock = Lock()
        self.water_cmd_buffer = []
        self.send_cmd_publisher = Publisher("AIPlanner_pub")
        self.last_water_time = None
        self.thread_terminate_flag = False

        self.db_handler = DB_handler("store.db")
        self.config = {}
        self.config_lock = Lock()
        self.accummulate_light_time = 0
        self.sunrise_data_date = None
        self.sunrise_time = None
        self.sunset_time = None

    def init(self):
        # init MQTT client
        self.mqtt_client.init()
        self.mqtt_client.set_function("on_message", self.on_message)
        self.send_cmd_publisher.init()

        # get config from database
        self.db_handler.init()
        self.config_lock.acquire()
        self.config = self.db_handler.get_config()
        self.config_lock.release()
        print("config: {}".format(json.dumps(self.config, indent=4)))

        # read last trigger time from file
        try:
            with open(self.last_time_file_path, 'r') as f:
                last_trigger_time_str = f.read()
                print("last_trigger_time_str: {}".format(last_trigger_time_str))
            self.last_trigger_time = datetime.datetime.strptime("")
        except:
            pass

    def start(self):
        try:
            # start a thread to handle command
            threading.Thread(target=self.send_command_thread).start()

            self.mqtt_client.start([(self.sensor_topic, 0), (self.config_topic, 0)])
        except KeyboardInterrupt:
            print("Process interrupted by user")
        except Exception as e:
            print(e)
        finally:
            self.thread_terminate_flag = True
        

    def send_command_thread(self):
        print("command thread start...")
        self.config_lock.acquire()
        single_light_time = self.config["single_light_time"]
        single_water_time = self.config["single_water_time"]
        self.config_lock.release()

        while not self.thread_terminate_flag:
            time.sleep(1)
            # print("light_cmd_buffer: {}".format(self.light_cmd_buffer))
            if len(self.light_cmd_buffer) > 0:
                sending_flag = self.last_light_time is None
                if self.last_light_time is not None:
                    delta = (datetime.datetime.now() - self.last_light_time).total_seconds()
                    minutes = delta*1.0/60
                    sending_flag = minutes > single_light_time
                if sending_flag:
                    self.light_cmd_buffer_lock.acquire()
                    cmd = self.light_cmd_buffer.pop(0)
                    self.light_cmd_buffer_lock.release()
                    # accumulate light time
                    add_flag = (self.last_light_cmd=="on")
                    now = datetime.datetime.now()
                    if self.sunrise_data_date is not None:
                        if now > self.sunrise_time and now < self.sunset_time:
                            add_flag = True
                    if add_flag and self.last_light_time is not None:
                        self.accummulate_light_time = int((now - self.last_light_time).total_seconds() / 60)

                    # convert to message format for MQTT
                    msg = ""
                    if cmd == "on":
                        msg = "circle_on"
                    else:
                        msg = "circle_off"
                    self.last_light_time = datetime.datetime.now()
                    self.last_light_cmd = cmd
                    self.send_cmd_publisher.publish(self.actuator_topic, msg)
                    print("actuator publish: {}".format(msg))
            
            # print("water_cmd_buffer: {}".format(self.water_cmd_buffer))
            if len(self.water_cmd_buffer) > 0:
                sending_flag = self.last_water_time is None
                if self.last_water_time is not None:
                    delta = (datetime.datetime.now() - self.last_water_time).total_seconds()
                    minutes = delta*1.0/60
                    sending_flag = minutes > single_water_time or self.water_cmd_buffer[0]=="on" # no need to wait if cmd is to turn on the water bump
                if sending_flag:
                    self.water_cmd_buffer_lock.acquire()
                    cmd = self.water_cmd_buffer.pop(0)
                    self.water_cmd_buffer_lock.release()
                    # convert to message format for MQTT
                    msg = ""
                    if cmd == "on":
                        msg = "circle_plus_on"
                    else:
                        msg = "circle_plus_off"
                    self.last_water_time = datetime.datetime.now()
                    self.send_cmd_publisher.publish(self.actuator_topic, msg)
                    print("actuator publish: {}".format(msg))

        
    def check_lightTime_enough_or_not_for_init_state(self):
        self.config_lock.acquire()
        enough_light_time = self.config["enough_light_time"]
        self.config_lock.release()

        now_time = datetime.datetime.now()
        today_datestring = now_time.strftime("%d.%m.%Y")
        if self.sunrise_data_date == today_datestring:
            return 
        self.sunrise_data_date, self.sunrise_time, self.sunset_time = self.db_handler.get_today_sun_data()
        if self.sunrise_data_date is None:
            return True # if no data, assume the light time is enough

        if now_time > self.sunrise_time and now_time < self.sunset_time:
            return True # if there is sun light, no need to consider light time
        
        if self.accummulate_light_time > enough_light_time:
            return True
        else:
            return False


    def check_trigger_or_not(self):
        now = datetime.datetime.now()
        if self.last_trigger_time is None:
            return True
        else:
            seconds = (now - self.last_trigger_time).total_seconds()
            minutes = seconds*1.0/60
            return  minutes > self.config["trigger_period"]
        
    def set_last_trigger_time(self):
        self.last_trigger_time = datetime.datetime.now()

        time_string = self.last_trigger_time.strftime("%d.%m.%Y, %H:%M:%S")
        with open(self.last_time_file_path, 'w') as f:
            f.write(time_string)


    def run_pyper_plan(self):
        process = subprocess.Popen(['/opt/homebrew/anaconda3/envs/sciot-env/bin/pyperplan', 'domain.pddl', 'problem.pddl'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        # print(stdout)

    def on_message(self, client, userdata, message):
        print("receive!")
        if message.topic == self.config_topic:
            self.config_lock.acquire()
            self.config = self.db_handler.get_config()
            self.config_lock.release()
            print("Updated config: {}".format(json.dumps(self.config, indent=4)))
        elif message.topic == self.sensor_topic:
            data = json.loads(message.payload.decode())
            if self.check_trigger_or_not():
                # generate init statement
                self.pddl_pb._init_list = [self.pddl_pb.light_is_off(self.pddl_pb.lights[1])]
                # generate light condition
                if self.check_lightTime_enough_or_not_for_init_state():
                    self.pddl_pb._init_list.append(self.pddl_pb.lightTime_is_enough(self.pddl_pb.lightTimes[1]))
                
                sensor_temp = data["Air Temperature"]
                if sensor_temp > float(self.config["max_temp"]):
                    self.pddl_pb._init_list.append(self.pddl_pb.temp_is_high(self.pddl_pb.temperatures[1]))
                elif sensor_temp > float(self.config["min_temp"]):
                    self.pddl_pb._init_list.append(self.pddl_pb.temp_is_ok(self.pddl_pb.temperatures[1]))
                else:
                    self.pddl_pb._init_list.append(self.pddl_pb.temp_is_low(self.pddl_pb.temperatures[1]))

                sensor_mois = data["Humidity"]
                if sensor_mois > float(self.config["max_mois"]):
                    self.pddl_pb._init_list.append(self.pddl_pb.moisture_is_high(self.pddl_pb.moistures[1]))
                elif sensor_mois > float(self.config["min_mois"]):
                    self.pddl_pb._init_list.append(self.pddl_pb.moisture_is_ok(self.pddl_pb.moistures[1]))
                else:
                    self.pddl_pb._init_list.append(self.pddl_pb.moisture_is_low(self.pddl_pb.moistures[1]))

                self.pddl_pb.generate_domain_pddl()
                self.pddl_pb.generate_problem_pddl()

                self.run_pyper_plan()

                # check if there is solution file or not
                now_path = pathlib.Path().resolve()
                file_list  = [f for f in listdir(now_path) if isfile(join(now_path, f))]
                solution = None
                if "problem.pddl.soln" in file_list:
                    solution_path = os.path.join(now_path, "problem.pddl.soln")
                    with open(solution_path, 'r')as f:
                        solution = f.readlines()
                    # os.remove(solution_path)
                    print(solution)
                else:
                    print("No solution file")

                if solution != None:
                    self.set_last_trigger_time()
                    # stored into sending buffer
                    for single_cmd in solution:
                        if "light-on" in single_cmd:
                            self.light_cmd_buffer_lock.acquire()
                            self.light_cmd_buffer.append("on")
                            self.light_cmd_buffer_lock.release()
                        elif "light-off" in single_cmd or "light-keep-off" in single_cmd:
                            self.light_cmd_buffer_lock.acquire()
                            self.light_cmd_buffer.append("off")
                            self.light_cmd_buffer_lock.release()
                        elif "water" in single_cmd:
                            self.water_cmd_buffer_lock.acquire()
                            self.water_cmd_buffer.append("on")
                            self.water_cmd_buffer.append("off")
                            self.water_cmd_buffer_lock.release()
    


if __name__ == "__main__":
    a = AIPlanner("sensor_data", "plugwise", "config")
    a.init()
    a.start()