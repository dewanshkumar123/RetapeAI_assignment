from vad import is_speech
from classifier import mentions_beep, greeting_finished

SILENCE_REQUIRED = 0.8

class Signal2:
    def __init__(self):
        self.last_speech_time = None
        self.detected = False

    def process(self, frame, transcript, current_time=0):
        """Process audio frame for greeting end detection.
        
        Args:
            frame: Audio frame (numpy array)
            transcript: STT transcript (string)
            current_time: Elapsed time in seconds
            
        Returns:
            bool: True if greeting finished, False otherwise
        """
        print("Transcript" ,transcript)   
        if self.detected:
            return False
        
        if is_speech(frame):
            self.last_speech_time = current_time
            return False
        
        # Check silence duration
        if self.last_speech_time is None:
            return False
        
        silence = current_time - self.last_speech_time
        
        if silence >= SILENCE_REQUIRED:
            if transcript and not mentions_beep(transcript):
                if greeting_finished(transcript):
                    self.detected = True
                    return True
        
        return False
