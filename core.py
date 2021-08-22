import os
import signal
import subprocess
import logging
from config import Config
from mqtt import Mqtt
from subprocess import PIPE, STDOUT
import time

from alarmserver import AlarmServer
from log import LogPipe

logger = logging.getLogger(__name__)

class Core:

    def __init__(self):
        self.config = Config()
        self.config.read()
        self.mqtt = Mqtt(self.config.mqtt_address, self.config.mqtt_port, self.config.mqtt_username, self.config.mqtt_password, self.config.mqtt_topic, self.config.mqtt_clientname)
        self.mqtt.subscribe('pyainvr/actions/stop', self.kill_all)
        self.mqtt.subscribe('pyainvr/actions/start', self.reload_config)
        
        logging.basicConfig()
        logger.setLevel(logging.WARNING)

        if self.config.alarmserver_enabled:
            logger.warn("Alarm server is enabled")
            AlarmServer(self.config.alarmserver_port, self.mqtt)

        self.reload_config()

    def kill_all(self):

         for cam in self.config.Cameras:
            cam.kill()

    def reload_config(self):
        
        # Kill existing process
        # self.kill_all()

        for cam in self.config.Cameras:
            cam.start(self.config)

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill_all()
        pass
    

