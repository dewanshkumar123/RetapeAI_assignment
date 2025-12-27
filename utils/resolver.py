class Resolver:
    def __init__(self):
        self.triggered = False
        self.reason = None
        self.beep_time = None

    def resolve(self, beep, signal2, timeout, beep_time=None):
        if self.triggered:
            return False

        if beep:
            self.reason = "BEEP"
            self.beep_time = beep_time
        elif signal2:
            self.reason = "GREETING_END"
        elif timeout:
            self.reason = "TIMEOUT"
        else:
            return False

        self.triggered = True
        return True
