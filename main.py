import time
from audio_stream import stream_audio
from stt import create_recognizer, feed_audio
from beep_detector import BeepDetector
from signal2 import Signal2
from timeout import Timeout
from resolver import Resolver
from vad import is_speech

AUDIO_FILE = "voicemails/vm6.wav"

beep = BeepDetector()
signal2 = Signal2()
timeout = Timeout(silence_duration=3.0)
resolver = Resolver()
recognizer = create_recognizer()

start = time.time()
elapsed = 0

for frame in stream_audio(AUDIO_FILE):
    transcript = feed_audio(recognizer, frame)
    
    # Get speech detection result
    speech_detected = is_speech(frame)

    beep_hit, beep_time = beep.process(frame, transcript, speech_detected, current_time=elapsed)
    s2_hit = signal2.process(frame, transcript, current_time=elapsed)
    timeout_hit = timeout.process(speech_detected, current_time=elapsed)

    if resolver.resolve(beep_hit, s2_hit, timeout_hit, beep_time=beep_time):
        print(
            f"Playback triggered at {elapsed:.2f}s "
            f"via {resolver.reason}"
        )
        if resolver.beep_time:
            print(f"Beep detected at {resolver.beep_time:.3f}s")
        break
    
    elapsed += 0.020  # 20ms frame duration
