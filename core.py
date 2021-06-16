import os
import subprocess
import logging
from config import Config
from mqtt import Mqtt

logger = logging.getLogger(__name__)

class Core:

    subs = []

    def start(self):
        self.reload_config()

    def reload_config(self):
        
        self.config = Config()
        self.config.read()
        
        # Kill existing process
        for sub in self.subs:
            sub.kill()

        
        #self.mqtt = Mqtt(self.config.mqtt_address, self.config.mqtt_port, self.config.mqtt_username, self.config.mqtt_password, self.config.mqtt_topic)

        for cam in self.config.Cameras:
            logger.info(f"Setting up camera {cam.name}")

            local_stream = f'rtsp://{self.config.rtsp_host}:8554/live/{cam.name}'
            cmd = f'ffmpeg \
                -loglevel {self.config.log_level} \
                -stimeout 1000000 \
                -use_wallclock_as_timestamps 1 \
                -rtsp_transport tcp \
                -i "{cam.stream}" \
                -rtsp_transport tcp \
                -c:v copy \
                -c:a copy \
                -f rtsp \
                {local_stream} '
            
            logger.info(f"Setting up recording")
            if cam.record:
                cmd = cmd + \
                f'-c copy \
                -c:a aac \
                -f segment \
                -segment_time {self.config.record_segment_length} \
                -segment_atclocktime 1 \
                -segment_format mp4 \
                -reset_timestamps 1 \
                -strftime 1 \
                "{self.config.record_dir}/{cam.name}_%Y%m%d_%H-%M-%S.mp4"'

            sub = subprocess.Popen(cmd)
            
            self.subs.append(sub)

    def __exit__(self, exc_type, exc_value, traceback):
        for sub in self.subs:
            sub.kill()
            
        pass