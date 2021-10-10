import os
import logging
import subprocess
import signal
from subprocess import PIPE, STDOUT
import time
from threading import Timer

from log import LogPipe

logger = logging.getLogger(__name__)

class Camera:

    def __init__(self, name, stream, actions, inputs, format, deviceid, config) -> None:
        
        self.name = name
        self.stream = stream

        self.rtmp = False
        self.rtsp = False
        self.record = False
        self.motion = False
        self.alarm = False

        if 'rtmp' in actions:
            self.rtmp = True

        if 'rtsp' in actions:
            self.rtsp = True

        if 'record' in actions:
            self.record = True

        if 'motion' in actions:
            self.motion = True

        if 'alarm' in actions:
            self.alarm = True
        
        self.inputs = inputs
        self.format = format
        self.config = config
        self.deviceid = deviceid

        self.logpipe = LogPipe(self.name, logging.INFO)

        pass


    def start(self):

        logger.warning(f"Setting up camera {self.name}")

        try:
            if self.proc.poll() is not None:
                logger.warning("Process has closed")
            else:
                logger.error("Recording already started")
                return
        except AttributeError:
            logger.warning("Camera process has not started")

        cmd = ['ffmpeg', 
            '-loglevel', self.config.log_level,
            '-stimeout', '5000000',
            '-fflags', '+genpts+discardcorrupt',
            '-use_wallclock_as_timestamps', '1',
            '-rtsp_transport', 'tcp',
            '-i', self.stream]

        if self.rtsp:
            rtsp_stream = f'rtsp://{self.config.rtsp_host}:8554/live/{self.name}'
            rtsp_cmd = ['-rtsp_transport', 'tcp',
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-f', 'rtsp',
                rtsp_stream]

            cmd = cmd + rtsp_cmd
            logger.warning(f"RTSP stream ready here: {rtsp_stream}")

        if self.rtmp:
            rtmp_stream = f'rtmp://{self.config.rtmp_host}:1936/live/{self.name}'
            rtmp_cmd = ['-c:v', 'copy',
                '-an',
                '-f', 'flv',
                rtmp_stream]

            cmd = cmd + rtmp_cmd
            logger.warning(f"RTMP stream ready here: {rtmp_stream}")

        if self.record:
            rec_cmd = [
            '-f', 'segment',
            '-segment_time', f'{self.config.record_segment_length}',
            '-segment_atclocktime', '1',
            '-segment_format', self.format,
            '-reset_timestamps', '1',
            '-strftime', '1',
            f'{os.path.join(self.config.record_dir, self.name, )}_%Y%m%d_%H-%M-%S.{self.format}']   

            cmd = cmd + self.inputs + rec_cmd
            logger.warning(f"Setting up recording")    

        logger.info(cmd)

        self.proc = subprocess.Popen(cmd, stdout = self.logpipe, stderr=self.logpipe)
    
    def hasStarted(self):
        try:
            if self.proc.poll() is not None:
                return False
        except AttributeError:
            return False
        
        return True
    
    def autoRecord(self):
        
        try:
            self.timer.cancel()
        except:
            self.timer = None
        
        if not self.hasStarted():
            self.start()
        
        self.timer = Timer(self.config.alarmserver_record_length, self.kill)
        self.timer.start()

    def kill(self):

        try:
            if not self.hasStarted():
                logger.warning("Process has closed")
                return

            os.kill(self.proc.pid, signal.SIGINT)
            logger.warning("Killing process")

            self.proc.communicate(timeout=30)
            logger.warning("Process killed")

        except subprocess.TimeoutExpired:
            logger.warning("ffmpeg not responding")
            self.proc.kill()
            self.proc.communicate()

        self.proc = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.logpipe.close()
        pass