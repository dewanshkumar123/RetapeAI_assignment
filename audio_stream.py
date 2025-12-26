import soundfile as sf
import resampy
import numpy as np

TARGET_SR = 16000
FRAME_MS = 20

def stream_audio(path):
    data, sr = sf.read(path)

    # Convert stereo to mono if needed
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Resample if needed
    if sr != TARGET_SR:
        data = resampy.resample(data, sr, TARGET_SR)
        sr = TARGET_SR

    frame_size = int(TARGET_SR * FRAME_MS / 1000)

    for i in range(0, len(data), frame_size):
        yield data[i:i + frame_size]
