import json
from vosk import Model, KaldiRecognizer

model = Model("models/vosk-model-small-en-us-0.15")

def create_recognizer(sr=16000):
    return KaldiRecognizer(model, sr)

def feed_audio(recognizer, frame):
    recognizer.AcceptWaveform((frame * 32768).astype("int16").tobytes())
    partial = json.loads(recognizer.PartialResult())
    return partial.get("partial", "")
