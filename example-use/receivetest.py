import paho.mqtt.client as mqtt
import json
import time

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor_data")

# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode()}")
    # 解析JSON数据
    data = json.loads(msg.payload.decode())
    print("Received data:", data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("conn before")
# 连接到本地MQTT Broker
client.connect_async('192.168.0.102', 1883, 60)
print("conn after")

# 启动客户端
client.loop_start()

# 让主线程保持运行
while True:
    time.sleep(1)
