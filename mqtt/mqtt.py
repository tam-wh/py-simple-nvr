import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)

class Mqtt:

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.subscriptions.keys():
            self.client.subscribe(topic, qos=0)
            
        logger.warning("Connected with result code "+str(rc))

    def on_publish(self, client,userdata,result):
        pass

    def on_message(self, client, userdata, message):
        logger.warning("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
        actionDict = self.subscriptions.get(message.topic)
        if actionDict != None:
            action = actionDict.get(str(message.payload.decode("utf-8")))
            if action != None:
                action()

    def __init__(self, address, port, username, password, clientname) -> None:

        self.address = address
        self.port = port

        self.client = mqtt.Client(clientname) 
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.username_pw_set(username=username,password=password)
        logger.info("Connecting...")

        self.subscriptions = {}
    
    def start(self):
        self.client.connect(self.address, self.port)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop() 
    
    def subscribe(self, topic, payload, action):
        if not topic in self.subscriptions:
            self.subscriptions[topic] = {}
        
        self.subscriptions[topic][payload] = action
    
    def publish(self, topic, payload):
        self.client.publish(topic, payload)  

