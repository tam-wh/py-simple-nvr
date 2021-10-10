import os
import signal
import subprocess
import logging
from config import Config
from mqtt import Mqtt
from subprocess import PIPE, STDOUT
import time

from alarmserver import AlarmServer

logger = logging.getLogger(__name__)

class Core:

    def __init__(self):
        self.config = Config()
        self.config.read()
        self.mqtt = Mqtt(self.config.mqtt_address, self.config.mqtt_port, self.config.mqtt_username, self.config.mqtt_password, self.config.mqtt_clientname)
        self.mqtt.subscribe('pyainvr/all/state/set', "off", self.kill_all)
        self.mqtt.subscribe('pyainvr/all/state/set', "on", self.start_all)

        logging.basicConfig()
        logger.setLevel(logging.WARNING)

        if self.config.alarmserver_enabled:
            logger.warn("Alarm server is enabled")
            AlarmServer(self.config.alarmserver_port, self.mqtt, self.config.Cameras)

        for cam in self.config.Cameras:
            self.mqtt.subscribe('pyainvr/' + cam.name + '/state/set', "off", cam.kill)
            self.mqtt.subscribe('pyainvr/' + cam.name + '/state/set', "on", cam.start)
            self.mqtt.subscribe('pyainvr/' + cam.name + '/state/set', "autorecord", cam.autoRecord)

        self.mqtt.start()
        self.start_all()
        

    def kill_all(self):
         for cam in self.config.Cameras:
            cam.kill()

    def start_all(self):
        for cam in self.config.Cameras:
            cam.start()
    
    def alarm_record(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill_all()
        pass
    