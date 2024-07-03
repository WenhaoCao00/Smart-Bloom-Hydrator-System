import paho.mqtt.client as mqtt
import json
import time
import queue
import threading
from plugwise.api import *


DEFAULT_PORT = "/dev/ttyUSB0"
circle_mac = "000D6F0004B1E8C0"
circle_plus_mac = "000D6F0004B1E8C0"

stick = Stick(DEFAULT_PORT)
circle = Circle(circle_mac, stick)
circle_plus = Circle(circle_plus_mac, stick)

# 创建一个队列来存储消息
message_queue = queue.Queue()

# 回调函数 - 当连接到服务器时调用
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("plugwise")

# 回调函数 - 当收到消息时调用
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"{msg.topic} Message: {message}")
    message_queue.put(message)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 连接到本地MQTT Broker
client.connect("localhost", 1883, 60)

# 启动客户端
client.loop_start()

def process_messages():
    while True:
        # 检查队列中是否有新消息
        if not message_queue.empty():
            message = message_queue.get()
            # 处理消息
            if message == "circle_on":
                print("Turning on the plugwise")
                circle.switch_on()
            elif message == "circle_off":
                print("Turning off the plugwise")
                circle.switch_off()
            elif message == "circle_plus_on":
                print("Turning on the plugwise plus")
                circle_plus.switch_on()
            elif message == "circle_plus_off":
                print("Turning off the plugwise plus")
                circle_plus.switch_off()
            else:
                print("Unknown message")
        time.sleep(1)

# 启动一个线程来处理消息
message_thread = threading.Thread(target=process_messages)
message_thread.start()

# 主线程可以继续执行其他任务
while True:
    time.sleep(8)
