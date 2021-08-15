import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)

class Mqtt:

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic,1)
        print("Connected with result code "+str(rc))

    def on_publish(self, client,userdata,result):
        print("Data published")
        pass

    def on_message(self, client, userdata, message):
        logger.warning("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
        action = self.subscriptions.get(message.topic)
        if action != None:
            action()

    def __init__(self, address, port, username, password, topic) -> None:
        
        self.topic = topic
        self.client = mqtt.Client("pyainvr") 
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.username_pw_set(username=username,password=password)
        print("Connecting...")
        self.client.connect(address, port)
        self.client.loop_start()

        self.subscriptions = {}

    def stop(self):
        self.client.loop_stop() 
    
    def subscribe(self, topic, action):
        self.subscriptions[topic] = action
        self.client.subscribe(topic, qos=0)

