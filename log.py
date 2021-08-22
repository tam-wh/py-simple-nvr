import logging
import threading
import os
import subprocess

logging.basicConfig(format='%(asctime)s  %(levelname)s\t[%(name)s]\t%(message)s', datefmt= "%Y-%m-%d %H:%M:%S", level=logging.INFO)

class LogPipe(threading.Thread):

    def __init__(self, name, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.logger = logging.getLogger(name)
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            self.logger.log(self.level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)