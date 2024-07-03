import paho.mqtt.client as mqtt

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("test_sensor_data")
    client.subscribe("weather_data")

# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 连接到本地MQTT Broker
client.connect("localhost", 1883, 60)

# 发布消息
def publish(topic, payload):
    client.publish(topic, payload)

# 启动客户端
client.loop_start()

# 发布测试消息
import time
while True:
    publish("sensor_data", "Sensor data message")
    #publish("weather_data", "Weather data message")
    time.sleep(5)
