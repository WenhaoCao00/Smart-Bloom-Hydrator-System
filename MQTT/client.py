import paho.mqtt.client as mqtt
import json

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("test_sensor_data")


# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message

# 连接到本地MQTT Broker
client.connect("localhost", 1883, 60)

# 发布消息
def publish(topic, payload):
    client.publish(topic, payload)

# 启动客户端
client.loop_start()


import time
while True:
    send_data = {
    'temperature': 30,
    'humidity': 50
    }
    dump_data = json.dumps(send_data)
    publish("test_sensor_data", dump_data)
    time.sleep(8)
