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
            logger.warning(f"Setting up camera {cam.name}")

            cmd = ['ffmpeg', 
                '-loglevel', self.config.log_level,
                '-stimeout', '1000000',
                '-fflags', '+genpts+discardcorrupt',
                '-use_wallclock_as_timestamps', '1',
                '-rtsp_transport', 'tcp',
                '-i', cam.stream]

            if cam.rtsp:
                rtsp_stream = f'rtsp://{self.config.rtsp_host}:8554/live/{cam.name}'
                rtsp_cmd = ['-rtsp_transport', 'tcp',
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    '-f', 'rtsp',
                    rtsp_stream]

                cmd = cmd + rtsp_cmd
                logger.warning(f"RTSP stream ready here: {rtsp_stream}")

            if cam.rtmp:
                rtmp_stream = f'rtmp://{self.config.rtmp_host}:1936/live/{cam.name}'
                rtmp_cmd = ['-c:v', 'copy',
                    '-an',
                    '-f', 'flv',
                    rtmp_stream]

                cmd = cmd + rtmp_cmd
                logger.warning(f"RTMP stream ready here: {rtmp_stream}")

            if cam.record:
                rec_cmd = [
                '-f', 'segment',
                '-segment_time', f'{self.config.record_segment_length}',
                '-segment_atclocktime', '1',
                '-segment_format', 'mp4',
                '-reset_timestamps', '1',
                '-strftime', '1',
                f'{os.path.join(self.config.record_dir, cam.name, )}_%Y%m%d_%H-%M-%S.mp4']   

                cmd = cmd + cam.inputs + rec_cmd
                logger.warning(f"Setting up recording")    

            logger.info(cmd)
            sub = subprocess.Popen(cmd)
            
            self.subs.append(sub)

    def __exit__(self, exc_type, exc_value, traceback):
        for sub in self.subs:
            sub.kill()
            
        pass