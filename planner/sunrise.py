import sqlite3
import requests
import json
import time
import datetime

sunrise_url = "https://api.sunrise-sunset.org/json"

class SunRiseAPI:
    def __init__(self, lat, lng, db_name, timezone_shift=2) -> None:
        self.lat = lat
        self.lng = lng
        self.timezone = 2

        self.db_name = db_name
        self.conn = None

    def init(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()

    def get_sunrise(self):
        try:
            r = requests.get(sunrise_url, params={"lat":self.lat, "lng":self.lng}, timeout=15)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                return None
        except:
            return None
        
    def parse_sun_string_to_datetime(self, s_string):
        add_hour = self.timezone
        if "PM" in s_string:
            add_hour += 12

        time_string = s_string.split(" ")[0]
        s_time = datetime.datetime.strptime(time_string, "%H:%M:%S")
        if add_hour > 0:
            return_time = s_time + datetime.timedelta(hours=add_hour)
        elif add_hour < 0:
            return_time = s_time - datetime.timedelta(hours=abs(add_hour))
        else:
            return_time = s_time
        return return_time
        
    def run(self):
        while True:
            # get database
            today_datestring = datetime.datetime.now().strftime("%d.%m.%Y")
            sql_cmd = """SELECT * FROM sunrise WHERE date = '{}';""".format(today_datestring)
            res = self.cur.execute(sql_cmd)
            result = res.fetchall()
            if len(result) == 0:
                # if no today's data, get one and write to db
                sunrise_data = self.get_sunrise()
                if sunrise_data is not None:
                    sunrise = sunrise_data["results"]["sunrise"]
                    sunrise = self.parse_sun_string_to_datetime(sunrise)
                    rise_str = sunrise.strftime("%H:%M:%S")
                    sunset = sunrise_data["results"]["sunset"]
                    sunset = self.parse_sun_string_to_datetime(sunset)
                    set_str = sunset.strftime("%H:%M:%S")

                    sql_cmd = """
                    INSERT INTO sunrise VALUES (?, ?, ?);
                    """
                    print("sql_cmd: {}".format(sql_cmd))
                    self.cur.executemany(sql_cmd, [(today_datestring, rise_str, set_str)])
                    self.conn.commit()
                
            time.sleep(20)

if __name__ == "__main__":
    sun_api = SunRiseAPI(48.74527114926762, 9.1062779405148, "store.db")
    sun_api.init()
    sun_api.run()
        
    