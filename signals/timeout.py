class Timeout:
    """
    Signal 3: Silence-based Timeout
    Triggers when silence_since exceeds threshold, but ONLY after at least one speech burst has been detected.
    """
    def __init__(self, silence_duration=3.0):
        self.silence_duration = silence_duration
        self.triggered = False
        self.speech_detected_once = False

    def process(self, is_speech, silence_since, current_time=0):
        if self.triggered:
            return False

        # Track if we've ever detected speech
        if is_speech:
            self.speech_detected_once = True
            return False

        # Don't count silence until we've heard at least one speech burst
        if not self.speech_detected_once:
            return False

        # Trigger if we've had sustained silence after speech has been detected
        if silence_since >= self.silence_duration:
            self.triggered = True
            return True

        return False

    def expired(self):
        return self.triggered
