import paho.mqtt.client as mqtt

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("config")

# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode()}")

client = mqtt.Client()
#client.on_connect = on_connect
#client.on_message = on_message

# 连接到本地MQTT Broker
client.connect('192.168.0.103', 1883, 60)

# 发布消息
def publish(topic, payload):
    client.publish(topic, payload)

# 启动客户端
client.loop_start()

# 发布测试消息
import time
config_d = {"max_temp":27, "min_temp":22, "max_mois":40, "min_mois":20, "enough_light_time":16*60, "single_water_time":0.1, "single_light_time":30, "trigger_period":60}
data = {"table_name": "config", "data": [config_d]}

#data to a json
import json
data = json.dumps(data)

while True:

    publish("db_data", data)
    time.sleep(3)
