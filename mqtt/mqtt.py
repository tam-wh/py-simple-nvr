import paho.mqtt.client as mqtt

class Mqtt:

    def on_connect(client, userdata, flags, rc):
        client.subscribe(self.topic,1)
        print("Connected with result code "+str(rc))

    def on_publish(client,userdata,result):
        print("Data published")
        pass

    def __init__(self, address, port, username, password, topic) -> None:
        
        self.topic = topic
        self.client = mqtt.Client("pyainvr") 
        self.client.on_connect = on_connect
        self.client.on_publish = on_publish
        self.client.username_pw_set(username=username,password=password)
        print("Connecting...")
        self.client.connect(address, port)
        self.client.loop_start()

    def stop():
        self.client.loop_stop() 