from dataclasses import dataclass

@dataclass
class TemperatureData:
    temp: float
    feels_like: float
    min: float
    max: float
    unit: str = "Kelvin"

    @classmethod
    def create_from_dict(cls, dict_data):
        temp = dict_data.get("temp", None)
        feels_like = dict_data.get("feels_like", None)
        min = dict_data.get("temp_min", None)
        max = dict_data.get("temp_max", None)
        return cls(temp, feels_like, min, max)
    
    def convert_unit_to_celsius(self):
        """This function is to convert the unit from Kelvin to Celsius
        """
        if self.unit == "Kelvin":
            attribute_names = ["temp", "feels_like", "min", "max"]
            for name in attribute_names:
                if type(self.__getattribute__(name)) == float:
                    self.__setattr__(name, self.__getattribute__(name)-273.15)
            self.unit = "Celsius"
        

@dataclass
class PressureData:
    pressure: float
    sea_level: float
    grand_level: float

    @classmethod
    def create_from_dict(cls, dict_data):
        pressure = dict_data.get("pressure", None)
        sea_level = dict_data.get("sea_level", None)
        grand_level = dict_data.get("grand_level", None)
        return cls(pressure, sea_level, grand_level)

@dataclass
class ForecastData:
    timestamp: int
    temp: TemperatureData
    pressure: PressureData
    humidity: float
    temp_kf: float

    weather: list
    clouds: dict
    wind: dict
    visibility: float
    pop: float
    sys: dict
    dt_txt: str

    @classmethod
    def create_from_dict(cls, dict_data):
        dt = dict_data.get("dt", None)
        main_data = dict_data.get("main", {})
        humidity = main_data.get("humidity", None)
        temp_kf = main_data.get("temp_kf", None)

        weather = dict_data.get("weather", [])
        clouds = dict_data.get("clouds", {})
        wind = dict_data.get("wind", {})
        visibility = dict_data.get("visibility", None)
        pop = dict_data.get("pop", None)
        sys = dict_data.get("sys", {})
        dt_txt = dict_data.get("dt_txt", "")

        td = TemperatureData.create_from_dict(main_data)
        td.convert_unit_to_celsius()
        pd = PressureData.create_from_dict(main_data)
        return cls(
            dt, td, pd,
            humidity, temp_kf,
            weather, clouds, wind, visibility,
            pop, sys, dt_txt
        )
