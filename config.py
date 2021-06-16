import yaml
from camera import Camera

class Config:

    def read(self):
        with open('config.yaml', 'r') as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)

        self.Cameras = []

        for cam in settings['cameras']:
            self.Cameras.append(Camera(cam['name'], cam['stream'], cam['actions']))
        
        self.rtsp_host = settings['global']['rtsp_host']
        self.record_dir = settings['global']['record_dir']
        self.record_segment_length = settings['global']['record_segment_length']
        self.log_level = settings['global']['log_level']

        self.mqtt_address = settings['mqtt']['address']
        self.mqtt_port = settings['mqtt']['port']
        self.mqtt_username = settings['mqtt']['username']
        self.mqtt_password = settings['mqtt']['password']
        self.mqtt_topic = settings['mqtt']['topic']

if __name__ == '__main__':
    Config().read()