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
data = {"table_name": "config", "data": [{"id": 2, "name": "sensor_data", "value": "1,2,3,4,5,6,7,8,9,10", "time": "2021-06-01 00:00:00"}, {"id": 2, "name": "sensor_data", "value": "1,2,3,4,5,6,7,8,9,10", "time": "2021-06-01 00:00:00"}]}
#data to a json
import json
data = json.dumps(data)
while True:

    publish("db_data", data)
    time.sleep(3)
