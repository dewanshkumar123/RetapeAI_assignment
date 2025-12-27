import os
import time
from audio_stream import stream_audio
from utils.stt import create_recognizer, feed_audio
from signals.beep import BeepDetector
from signals.message_end import MessageEnd
from signals.timeout import Timeout
from utils.resolver import Resolver
from utils.vad import is_speech

VOICEMAILS_DIR = "voicemails"

# List all .wav files in the voicemails directory
voicemail_files = [f for f in os.listdir(VOICEMAILS_DIR) if f.lower().endswith('.wav')]

if not voicemail_files:
    print("No voicemail files found in the folder.")
else:
    for filename in sorted(voicemail_files):
        audio_path = os.path.join(VOICEMAILS_DIR, filename)
        print(f"\nProcessing file: {audio_path}")
        beep = BeepDetector()
        signal2 = MessageEnd()
        timeout = Timeout(silence_duration=3.0)
        resolver = Resolver()
        recognizer = create_recognizer()
        start = time.time()
        elapsed = 0
        triggered = False
        for frame in stream_audio(audio_path):
            transcript = feed_audio(recognizer, frame)
            speech_detected = is_speech(frame)
            beep_hit, beep_time = beep.process(frame, transcript, speech_detected, current_time=elapsed)
            s2_hit = signal2.process(frame, transcript, current_time=elapsed)
            timeout_hit = timeout.process(speech_detected, current_time=elapsed)
            if resolver.resolve(beep_hit, s2_hit, timeout_hit, beep_time=beep_time):
                print(f"Playback triggered at {elapsed:.2f}s via {resolver.reason}")
                if resolver.beep_time:
                    print(f"Beep detected at {resolver.beep_time:.3f}s")
                triggered = True
                break
            elapsed += 0.020  # 20ms frame duration
        if not triggered:
            print("No playback triggered for this file.")
