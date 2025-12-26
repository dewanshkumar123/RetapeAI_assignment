from classifier import mentions_beep

class Timeout:
    """
    Signal 3: Conservative Timeout with Silence Detection
    
    This is the final fallback when beep detection and greeting-end detection fail.
    
    Strategy:
    1. Detect sustained silence (no speech detected)
    2. Only trigger if no beep keywords mentioned in transcript
    3. Use a configurable silence duration threshold (default 2 seconds)
    4. Fall back to absolute max time limit (default 10 seconds) as safety net
    """
    
    def __init__(self, silence_duration=2.0, max_seconds=15):
        """
        Args:
            silence_duration: How long (seconds) of silence before triggering (default 2s)
            max_seconds: Absolute maximum time limit before forced trigger (default 10s)
        """
        self.silence_duration = silence_duration
        self.max_seconds = max_seconds
        self.silence_start = None
        self.elapsed = 0
        self.triggered = False
        
    def process(self, is_speech, transcript, current_time=0):
        """
        Process frame for timeout trigger.
        
        Args:
            is_speech: Boolean indicating if speech is detected in current frame
            transcript: STT transcript string
            current_time: Elapsed time in seconds
            
        Returns:
            bool: True if timeout should trigger, False otherwise
        """
        if self.triggered:
            return False
        
        self.elapsed = current_time
        
        # Check absolute max time (safety net)
        if current_time >= self.max_seconds:
            print("heyyyyyy")
            self.triggered = True
            return True
        
        # Check if beep is mentioned - if so, don't timeout (beep is coming)
        if transcript and mentions_beep(transcript):
            self.silence_start = None
            return False
        
        # Track silence duration
        if is_speech:
            # Speech detected - reset silence counter
            self.silence_start = None
            return False
        else:
            # No speech (silence or noise)
            if self.silence_start is None:
                self.silence_start = current_time
            
            silence_duration = current_time - self.silence_start
            
            # Trigger if we've had sustained silence
            if silence_duration >= self.silence_duration:
                print("Exceeds silence dur")
                self.triggered = True
                return True
        
        return False
    
    def expired(self):
        """Backward compatible method for old code."""
        return self.triggered
