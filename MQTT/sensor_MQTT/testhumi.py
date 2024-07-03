import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from openzwave.node import ZWaveNode

import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)

device_name = "/dev/ttyACM0"


options = ZWaveOption(device_name, config_path="/home/pi/iot-ws/openzwave/config", user_path=".")
options.set_console_output(False)
options.lock()

network = ZWaveNetwork(options)
network.start()

while network.state != network.STATE_READY:
    time.sleep(1)
    logging.info("Network not ready...")

logging.info("Network is ready!!!")

logging.info("========= Setup Param =========")
for node in network.nodes:
    network.nodes[node].set_config_param(111, 10)
time.sleep(0.5)

while True:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_lines = [timestamp]
    
    for node in network.nodes:
        for val in network.nodes[node].get_sensors():
            label = network.nodes[node].values[val].label
            data = network.nodes[node].values[val].data
            if label in ["Air Temperature", "Illuminance","Humidity", "Ultraviolet"]:
                data_lines.append(f"{label}: {data}")
    
    with open("sensor_data.txt", "a") as file:
        for line in data_lines:
            file.write(line + "\n")
        file.write("---------------------------------\n")
    
    for line in data_lines:
        print(line)
    print("---------------------------------")
    
    time.sleep(3)  #collect data every 3 seconds


# node/name/index/instance : 2//0/1
#   label/help : Sensor/Binary Sensor State
#   id on the network : c80d28e3.2.30.1.0
#   value: True
#   data: True
# node/name/index/instance : 2//1/1
#   label/help : Air Temperature/Air Temperature Sensor Value
#   id on the network : c80d28e3.2.31.1.1
#   value: 24.700000762939453 C
#   data: 24.700000762939453
# node/name/index/instance : 2//3/1
#   label/help : Illuminance/Luminance Sensor Value
#   id on the network : c80d28e3.2.31.1.3
#   value: 86.0 Lux
#   data: 86.0
# node/name/index/instance : 2//5/1
#   label/help : Humidity/Humidity Sensor Value
#   id on the network : c80d28e3.2.31.1.5
#   value: 71.0 %
#   data: 71.0
# node/name/index/instance : 2//27/1
#   label/help : Ultraviolet/Ultraviolet Sensor Value
#   id on the network : c80d28e3.2.31.1.27
#   value: 0.0 UV
#   data: 0.0
