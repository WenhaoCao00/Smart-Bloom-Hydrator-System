import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from openzwave.node import ZWaveNode



import logging
import time
import json

import paho.mqtt.client as mqtt
#pip install paho-mqtt python-etcd

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor_data")

# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message

# 连接到本地MQTT Broker
client.connect_async("192.168.0.106", 1883, 60)

# 发布消息
def publish(topic, payload):
    client.publish(topic, payload)

# 启动客户端
client.loop_start()




logging.basicConfig(level=logging.INFO)

device_name = "/dev/ttyACM0"

options = ZWaveOption(device_name, config_path="/home/pi/python-openzwave/openzwave/config", user_path=".")

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
    publish_content = {}
    
    for node in network.nodes:
        for val in network.nodes[node].get_sensors():
            label = network.nodes[node].values[val].label
            data = network.nodes[node].values[val].data
            if label in ["Air Temperature", "Illuminance", "Humidity", "Ultraviolet"]:
                if label == "Air Temperature":
                    data = round(data, 1)  # 保留一位小数
                publish_content[label] = data


    
    dump_data = json.dumps(publish_content)
    publish("sensor_data", dump_data)
    
    time.sleep(10) 


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
