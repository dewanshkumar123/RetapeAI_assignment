import webrtcvad
import numpy as np

vad = webrtcvad.Vad(3)

def is_speech(frame, sample_rate=16000):
    """Detect speech in audio frame using WebRTC VAD.
    
    Args:
        frame: numpy array of audio samples (float32, -1.0 to 1.0)
        sample_rate: sample rate in Hz (must be 8000, 16000, 32000, or 48000)
        
    Returns:
        bool: True if speech detected, False otherwise
    """
    if len(frame) == 0:
        return False
    
    try:
        # Validate frame length is correct for VAD (10, 20, 30, or 40 ms)
        expected_samples = sample_rate // 100  # 10ms minimum
        if len(frame) < expected_samples:
            return False
        
        # Convert float32 [-1, 1] to int16 PCM [-32768, 32767]
        pcm = np.clip(frame, -1.0, 1.0) * 32768
        pcm = pcm.astype(np.int16).tobytes()
        
        return vad.is_speech(pcm, sample_rate)
    except Exception:
        # If VAD fails, assume speech (conservative approach)
        return True
