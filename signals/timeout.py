class Timeout:
    """
    Signal 3: Silence-based Timeout
    
    Triggers when 3 seconds of sustained silence is detected,
    but ONLY after at least one speech burst has been detected.
    
    This prevents triggering on initial silence before voicemail greeting starts.
    """
    
    def __init__(self, silence_duration=3.0):
        """
        Args:
            silence_duration: Silence duration before triggering (default 3s)
        """
        self.silence_duration = silence_duration
        self.silence_start = None
        self.triggered = False
        self.speech_detected_once = False  # Track if we've heard speech at least once
        
    def process(self, is_speech, current_time=0):
        """
        Process frame for timeout trigger.
        
        Args:
            is_speech: Boolean indicating if speech is detected
            current_time: Elapsed time in seconds
            
        Returns:
            bool: True if timeout should trigger, False otherwise
        """
        if self.triggered:
            return False
        
        # Track if we've ever detected speech
        if is_speech:
            self.speech_detected_once = True
            # Speech detected - reset silence counter
            self.silence_start = None
            return False
        
        # Don't count silence until we've heard at least one speech burst
        if not self.speech_detected_once:
            return False
        
        # No speech (silence or noise) - and we've heard speech before
        if self.silence_start is None:
            self.silence_start = current_time
        
        silence_duration = current_time - self.silence_start
        
        # Trigger if we've had sustained silence after speech has been detected
        if silence_duration >= self.silence_duration:
            self.triggered = True
            return True
        
        return False
    
    def expired(self):
        """Backward compatible method for old code."""
        return self.triggered
