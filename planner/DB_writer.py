import sqlite3
from MQTTClient import *
import datetime

class DBWriter:
    def __init__(self, db_name, sensor_topic, actuator_topic, config_topic) -> None:
        self.mqtt_client = Listener("db_writer")
        self.sensor_topic = sensor_topic
        self.actuator_topic = actuator_topic
        self.config_topic = config_topic

        self.db_name = db_name 
        self.conn = None

    def init_and_start(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()
        self.create_table()

        self.mqtt_client.init()
        self.mqtt_client.set_function("on_message", self.on_message)
        self.mqtt_client.start([(self.sensor_topic,0), (self.actuator_topic,0), (self.config_topic,0)])

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
            
if __name__ == "__main__":
    dw = DBWriter("store.db", "sensor_data", "plugwise", "config")
    dw.init_and_start()
