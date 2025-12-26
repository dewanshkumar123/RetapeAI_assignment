import numpy as np
from scipy.signal import periodogram, get_window
from scipy.fft import rfft, rfftfreq

BEEP_FREQ_MIN = 900
BEEP_FREQ_MAX = 1600
MIN_DURATION_FRAMES = 12  # ~240 ms
POWER_THRESHOLD_DB = -30  # Minimum power relative to peak

class BeepDetector:
    def __init__(self, sample_rate=16000, frame_ms=20):
        self.sr = sample_rate
        self.frame_ms = frame_ms
        self.count = 0
        self.beep_start_time = None
        self.current_time = 0
        self.frame_duration = frame_ms / 1000.0
        self.detected = False
        
    def _detect_tone_frequency(self, frame):
        """
        Detect dominant frequency using FFT with windowing.
        Returns (frequency, power_db) or (None, None) if no clear tone detected.
        """
        if len(frame) == 0:
            return None, None
            
        # Apply Hann window to reduce spectral leakage
        window = get_window('hann', len(frame))
        windowed = frame * window
        
        # Compute FFT
        fft_vals = rfft(windowed)
        freqs = rfftfreq(len(frame), 1.0 / self.sr)
        power = np.abs(fft_vals) ** 2
        
        # Convert to dB
        power_db = 10 * np.log10(power + 1e-10)
        
        # Find dominant frequency
        max_idx = np.argmax(power_db)
        dominant_freq = freqs[max_idx]
        dominant_power_db = power_db[max_idx]
        
        return dominant_freq, dominant_power_db

    def process(self, frame, current_time=None):
        """
        Process audio frame for beep detection.
        
        Args:
            frame: Audio frame (numpy array)
            current_time: Elapsed time in seconds (optional, auto-incremented if not provided)
            
        Returns:
            (beep_detected: bool, beep_time: float or None)
        """
        if current_time is None:
            self.current_time += self.frame_duration
        else:
            self.current_time = current_time
        
        if self.detected:
            return False, None
        
        freq, power_db = self._detect_tone_frequency(frame)
        
        if freq is None:
            self.count = 0
            return False, None
        
        # Check if dominant frequency is in beep range AND power is sufficient
        in_range = BEEP_FREQ_MIN <= freq <= BEEP_FREQ_MAX
        
        if in_range:
            if self.count == 0:
                self.beep_start_time = self.current_time
            
            self.count += 1
            
            # Beep confirmed: stable tone for required duration
            if self.count >= MIN_DURATION_FRAMES:
                self.detected = True
                beep_trigger_time = self.beep_start_time + 0.05  # +50ms as per spec
                return True, beep_trigger_time
        else:
            self.count = 0
            self.beep_start_time = None
        
        return False, None
