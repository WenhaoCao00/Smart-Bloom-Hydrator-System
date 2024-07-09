import sqlite3
from MQTTClient import *
import datetime

table_column_dict = {
    "config": ["max_temp", "min_temp", "max_mois", "min_mois", "enough_light_time", "single_water_time", "single_light_time", "trigger_period"],
    "sensor_record": ["time", "type", "value"],
    "actuator_record": ["time", "action"],
    "sunrise": ["date", "sunrise", "sunset"],
}

class DBHandler:
    def __init__(self, db_name, sensor_topic, actuator_topic, config_topic, get_data_topic, return_data_topic) -> None:
        self.mqtt_client = Listener("db_handler", "")
        self.mqtt_publisher = Publisher("gd_handler_sender", "")
        self.sensor_topic = sensor_topic
        self.actuator_topic = actuator_topic
        self.config_topic = config_topic
        self.get_data_topic = get_data_topic
        self.return_data_topic = return_data_topic

        self.db_name = db_name 
        self.conn = None

    def init_and_start(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()
        self.create_table()

        self.mqtt_publisher.init()
        self.mqtt_client.init()
        self.mqtt_client.set_function("on_message", self.on_message)
        self.mqtt_client.start([(self.sensor_topic,0), (self.actuator_topic,0), (self.config_topic,0), (self.get_data_topic,0)])

    def create_table(self):
        sql_cmd = """
        CREATE TABLE IF NOT EXISTS config (max_temp, min_temp, max_mois, min_mois, enough_light_time, single_water_time, single_light_time, trigger_period); 
        """
        self.cur.execute(sql_cmd)
        sql_cmd = """SELECT * FROM config;"""
        res = self.cur.execute(sql_cmd)
        result = res.fetchall()
        if len(result) == 0:
            sql_cmd = """INSERT INTO config VALUES ('', '', '', '', '', '', '', '');"""
            self.cur.execute(sql_cmd)
            self.conn.commit()

        sql_cmd = """CREATE TABLE IF NOT EXISTS sensor_record (time, type, value);"""
        self.cur.execute(sql_cmd)

        sql_cmd = """CREATE TABLE IF NOT EXISTS actuator_record (time, action);"""
        self.cur.execute(sql_cmd)

        sql_cmd = """CREATE TABLE IF NOT EXISTS sunrise (date, sunrise, sunset);"""
        self.cur.execute(sql_cmd)

    def on_message(self, client, userdata, message):
        print("receive: {}".format(message.payload.decode()))
        now = datetime.datetime.now()
        time_str = now.strftime("%d.%m.%Y, %H:%M:%S")
        if message.topic == self.sensor_topic:
            data = json.loads(message.payload.decode())
            sql_cmd = """
            INSERT INTO sensor_record VALUES (?, ?, ?);
            """

            insert_data = []
            for d in data:
                insert_data.append((time_str, d, data[d]))
            print("sql_cmd: {}".format(sql_cmd))
            self.cur.executemany(sql_cmd, insert_data)
            self.conn.commit()

        elif message.topic == self.actuator_topic:
            data = message.payload.decode()
            sql_cmd = """
            INSERT INTO actuator_record VALUES (?, ?);
            """
            print("sql_cmd: {}".format(sql_cmd))
            self.cur.executemany(sql_cmd, [(time_str, data)])
            self.conn.commit()
        elif message.topic == self.config_topic:
            data = json.loads(message.payload.decode())
            tmp_sql_cmd = """
            UPDATE config SET 
            """
            for key in data:
                tmp_sql_cmd += "{}={},".format(key, data[key])
            sql_cmd = tmp_sql_cmd[:-1] + ";"
            print("sql_cmd: {}".format(sql_cmd))
            self.cur.execute(sql_cmd)
            self.conn.commit()
        elif message.topic == self.get_data_topic:
            table_name = message.payload.decode()
            if table_name in table_column_dict:
                sql_cmd = """
                SELECT * FROM {};
                """.format(table_name)
                res = self.cur.execute(sql_cmd)
                result = res.fetchall()

                return_data = {"table_name": table_name, "data":[]}
                for tuple_d in result:
                    single_dict = {}
                    for i, key in enumerate(table_column_dict[table_name]):
                        single_dict[key] = tuple_d[i]
                    return_data["data"].append(single_dict)
                self.mqtt_publisher.publish(self.return_data_topic, return_data)

            
if __name__ == "__main__":
    dw = DBHandler("store.db", "sensor_data", "plugwise", "config", "get_db", "db_data")
    dw.init_and_start()
