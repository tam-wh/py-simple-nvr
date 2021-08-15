import os
import signal
import subprocess
import logging
import asyncio
from config import Config
from mqtt import Mqtt
from subprocess import PIPE, STDOUT
import time

logger = logging.getLogger(__name__)

class Core:

    subs = []

    def start(self):
        self.config = Config()
        self.config.read()
        self.mqtt = Mqtt(self.config.mqtt_address, self.config.mqtt_port, self.config.mqtt_username, self.config.mqtt_password, self.config.mqtt_topic)
        self.mqtt.subscribe('pyainvr/actions/stop', self.kill_all)
        self.mqtt.subscribe('pyainvr/actions/start', self.reload_config)

        self.reload_config()

    def kill_all(self):
        for sub in self.subs:
            os.kill(sub.pid, signal.SIGINT)
            sub.wait()
            logger.warning("Killing process")

        self.subs.clear()

    def log_subprocess_output(self, pipe):
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            logger.info('got line from subprocess: %r', line)

    def run_cam(self, cam):
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

        # proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        # self.subs.append(proc)
        # stdout, stderr = await proc.communicate()

        # logger.info(f'[{cmd!r} exited with {proc.returncode}]')
        # if stdout:
        #     logger.info(f'[stdout]\n{stdout.decode()}')
        # if stderr:
        #     logger.info(f'[stderr]\n{stderr.decode()}')

        sub = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)            
        self.subs.append(sub)

        # with sub.stdout:
        #     self.log_subprocess_output(sub.stdout)

    def reload_config(self):
        
        # Kill existing process
        self.kill_all()

        for cam in self.config.Cameras:
            self.run_cam(cam)

        # tasks = []
        # for cam in self.config.Cameras:
        #     tasks.append(asyncio.create_task(self.run_cam(cam)))
        
        # await asyncio.gather(*tasks)


    def __exit__(self, exc_type, exc_value, traceback):
        self.kill_all()
        pass

