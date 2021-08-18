import logging
import subprocess
from subprocess import PIPE, STDOUT

from log import LogPipe

logger = logging.getLogger(__name__)

class Camera:

    def __init__(self, name, stream, actions, inputs) -> None:
        
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
            
        pass


    def start(self, cam, config):

        logger.warning(f"Setting up camera {cam.name}")
        self.logpipe = LogPipe(cam.name, logging.INFO)

        cmd = ['ffmpeg', 
            '-loglevel', config.log_level,
            '-stimeout', '1000000',
            '-fflags', '+genpts+discardcorrupt',
            '-use_wallclock_as_timestamps', '1',
            '-rtsp_transport', 'tcp',
            '-i', cam.stream]

        if cam.rtsp:
            rtsp_stream = f'rtsp://{config.rtsp_host}:8554/live/{cam.name}'
            rtsp_cmd = ['-rtsp_transport', 'tcp',
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-f', 'rtsp',
                rtsp_stream]

            cmd = cmd + rtsp_cmd
            logger.warning(f"RTSP stream ready here: {rtsp_stream}")

        if cam.rtmp:
            rtmp_stream = f'rtmp://{config.rtmp_host}:1936/live/{cam.name}'
            rtmp_cmd = ['-c:v', 'copy',
                '-an',
                '-f', 'flv',
                rtmp_stream]

            cmd = cmd + rtmp_cmd
            logger.warning(f"RTMP stream ready here: {rtmp_stream}")

        if cam.record:
            rec_cmd = [
            '-f', 'segment',
            '-segment_time', f'{config.record_segment_length}',
            '-segment_atclocktime', '1',
            '-segment_format', 'mp4',
            '-reset_timestamps', '1',
            '-strftime', '1',
            f'{os.path.join(config.record_dir, cam.name, )}_%Y%m%d_%H-%M-%S.mp4']   

            cmd = cmd + cam.inputs + rec_cmd
            logger.warning(f"Setting up recording")    

        logger.info(cmd)

        self.proc = subprocess.Popen(cmd, stdout = self.logpipe, stderr=self.logpipe)
    
    def kill(self):
        self.logpipe.close()
        os.kill(self.proc.pid, signal.SIGINT)
        proc.wait()
        logger.warning("Killing process")