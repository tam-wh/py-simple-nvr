
class Camera:

    def __init__(self, name, stream, actions) -> None:
        
        self.name = name
        self.stream = stream

        self.record = False
        self.motion = False
        self.alarm = False

        if 'record' in actions:
            self.record = True

        if 'motion' in actions:
            self.motion = True

        if 'alarm' in actions:
            self.alarm = True
            
        pass

