from utils.vad import is_speech
from utils.classifier import mentions_beep, greeting_finished

SILENCE_CONFIRMATION = 1  # Silence duration to confirm greeting end is real

class MessageEnd:
    def __init__(self):
        self.detected = False
        self.greeting_detected = False
        self.detected_phrase = None

    def process(self, frame, transcript, speech_detected, silence_since, current_time=0):
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
        # print(silence_since, transcript)
        if self.detected:
            return False


        # If greeting detected and enough silence has passed, trigger
        if self.greeting_detected and silence_since >= SILENCE_CONFIRMATION:
            self.detected = True
            return True

        # Only process if no beep is expected (if beep expected, let beep detector handle it)
        if transcript and mentions_beep(transcript):
            self.greeting_detected = False
            self.detected_phrase = None
            return False

        # Check for greeting finished in transcript
        if transcript and greeting_finished(transcript):
            self.greeting_detected = True
            # Extract detected phrase
            from utils.classifier import END_GREETING_KEYWORDS, CONVERSATION_ENDERS
            t = transcript.lower()
            self.detected_phrase = None
            for k in END_GREETING_KEYWORDS:
                if k in t:
                    self.detected_phrase = k
                    break
            if not self.detected_phrase:
                import re
                for pattern in CONVERSATION_ENDERS:
                    m = re.search(pattern, t)
                    if m:
                        self.detected_phrase = m.group(0)
                        break
            return False

        # If speech resumes, reset greeting detection
        if speech_detected and self.greeting_detected:
            self.greeting_detected = False
            self.detected_phrase = None
            return False

        return False
