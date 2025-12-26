from vad import is_speech
from classifier import mentions_beep, greeting_finished

SILENCE_CONFIRMATION = 0.8  # Silence duration to confirm greeting end is real

class Signal2:
    def __init__(self):
        self.detected = False
        self.greeting_detected = False
        self.silence_start = None

    def process(self, frame, transcript, current_time=0):
        """Process audio frame for greeting end detection.
        
        Logic:
        1. Detect greeting/end of sentence in transcript
        2. Wait for 0.8s of continuous silence after greeting detected
        3. If speech resumes within 0.8s window, it was false alarm - reset and wait for another greeting
        4. Only trigger after 0.8s of uninterrupted silence confirmed
        
        Args:
            frame: Audio frame (numpy array)
            transcript: STT transcript (string)
            current_time: Elapsed time in seconds
            
        Returns:
            bool: True if greeting + 0.8s continuous silence confirmed, False otherwise
        """
        if self.detected:
            return False
        
        speech = is_speech(frame)
        
        # Only process if no beep is expected (if beep expected, let beep detector handle it)
        if transcript and mentions_beep(transcript):
            # Reset if beep is mentioned
            self.greeting_detected = False
            self.silence_start = None
            return False
        
        # Case 1: Speech detected
        if speech:
            # Check for greeting finished in transcript
            if transcript and greeting_finished(transcript):
                # Greeting detected - start listening for 0.8s silence
                self.greeting_detected = True
                self.silence_start = None  # Reset silence counter, will start on next silence frame
                return False
            
            # Speech detected but no greeting - this is a false alarm if we were waiting
            if self.greeting_detected:
                # Speech resumed within the 0.8s window - false alarm!
                # Reset and wait for another greeting
                self.greeting_detected = False
                self.silence_start = None
            
            return False
        
        # Case 2: Silence detected (no speech)
        # Only process if greeting was already detected
        if not self.greeting_detected:
            return False
        
        # Start silence countdown when silence begins after greeting
        if self.silence_start is None:
            self.silence_start = current_time
        
        silence_duration = current_time - self.silence_start
        
        # Check for continuous 0.8s silence after greeting
        if silence_duration >= SILENCE_CONFIRMATION:
            self.detected = True
            return True
        
        return False
