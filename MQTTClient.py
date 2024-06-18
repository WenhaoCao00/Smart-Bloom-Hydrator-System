import time
from datetime import datetime
import json
import paho.mqtt.client as mqtt

class Publisher:
    def __init__(self, name, server_ip='127.0.0.1', server_port=1883):
        self.name = name
        self.server_ip = server_ip
        self.server_port = server_port

        self.mqtt_publisher = None
        
    def init(self):
        self.mqtt_publisher = mqtt.Client(client_id=self.name)
        self.mqtt_publisher.connect(self.server_ip, self.server_port, 70)
        self.mqtt_publisher.loop_start()

    def publish(self, topic, message):
        send_msg = message
        if type(message) != str:
            send_msg = json.dumps(message)
        
        if self.mqtt_publisher is not None:
            self.mqtt_publisher.publish(topic, send_msg)


class Listener:
    def __init__(self, name, server_ip='127.0.0.1', server_port=1883):
        self.name = name
        self.server_ip = server_ip
        self.server_port = server_port

        self.mqtt_subscriber = None
    
    def init(self):
        self.mqtt_subscriber = mqtt.Client(client_id=self.name)
        self.mqtt_subscriber.on_message = self.on_message
        self.mqtt_subscriber.on_connect = self.on_connect

    def on_message(self, client, userdata, message):
        print('Message topic {}'.format(message.topic))
        print('Message payload:')
        print(json.loads(message.payload.decode()))

    def on_connect(self, *args, **kwargs):
        print("Connect to server!")

    def start(self, target_topic):
        if self.mqtt_subscriber is not None:
            self.mqtt_subscriber.connect(self.server_ip, self.server_port, 70)
            self.mqtt_subscriber.subscribe(target_topic)
            self.mqtt_subscriber.loop_forever()
        