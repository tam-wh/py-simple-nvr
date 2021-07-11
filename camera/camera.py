
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

