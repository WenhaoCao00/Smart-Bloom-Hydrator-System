import json
import requests

from weather_dataclass import *

API_KEY = ""

# The lantituge and longitude
LAN = 48.74527114926762
LON = 9.1062779405148

class WeatherForecast:
    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def get_forcast(self, target_position: tuple) -> dict:
        # TODO: finalize the return type
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        
        param = {
            "appid": self.api_key,
            "lat": target_position[0],
            "lon": target_position[1]
        }

        try:
            r = requests.get(base_url, params=param)
            r = r.text
        except Exception as e:
            print(e)
            return None
        
        return r
    
if __name__ == "__main__":
    wf = WeatherForecast(API_KEY)
    res = wf.get_forcast((LAN , LON))
    json_res = json.loads(res)

    a = ForecastData.create_from_dict(json_res["list"][0])
    print(a)