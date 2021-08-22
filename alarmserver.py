import struct, json
import threading
import logging
from time import sleep
from socket import *

logger = logging.getLogger(__name__)

class AlarmServer(threading.Thread):

    def __init__(self, port, mqtt_client):

        threading.Thread.__init__(self)
        self.daemon = True

        self.port = port
        self.mqtt_client = mqtt_client

        self.start()
    
    def run(self):

        server = socket(AF_INET, SOCK_STREAM)
        server.bind(("0.0.0.0", int(self.port)))
        server.listen(1)

        logger.warn("Listening to alarm server")

        while True:
            try:
                conn, addr = server.accept()
                head, version, session, sequence_number, msgid, len_data = struct.unpack(
                    "BB2xII2xHI", conn.recv(20)
                )
                sleep(0.1)  # Just for recive whole packet
                data = conn.recv(len_data)
                conn.close()
                
                jdata = json.loads(data.decode('utf-8'))

                device_name = jdata['SerialID']
                mqtt_topic = 'cameras/' + device_name

                self.mqtt_client.publish(mqtt_topic,json.dumps(jdata))  

            except (KeyboardInterrupt, SystemExit):
                break
        
        server.close()
