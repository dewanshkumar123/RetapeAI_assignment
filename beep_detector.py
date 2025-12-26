# import numpy as np
# from scipy.signal import periodogram, get_window
# from scipy.fft import rfft, rfftfreq
# from classifier import mentions_beep

# BEEP_FREQ_MIN = 900
# BEEP_FREQ_MAX = 1600
# MIN_DURATION_FRAMES = 12  # ~240 ms
# EXPECTED_BEEP_TIMEOUT = 3.0  # If beep is expected but no beep in 3s silence, trigger anyway

# class BeepDetector:
#     def __init__(self, sample_rate=16000, frame_ms=20):
#         self.sr = sample_rate
#         self.frame_ms = frame_ms
#         self.count = 0
#         self.beep_start_time = None
#         self.current_time = 0
#         self.frame_duration = frame_ms / 1000.0
#         self.detected = False
#         self.beep_expected = False
#         self.silence_start = None
        
#     def _detect_tone_frequency(self, frame):
#         """
#         Detect dominant frequency using FFT with windowing.
#         Returns (frequency, power_db) or (None, None) if no clear tone detected.
#         """
#         if len(frame) == 0:
#             return None, None
            
#         # Apply Hann window to reduce spectral leakage
#         window = get_window('hann', len(frame))
#         windowed = frame * window
        
#         # Compute FFT
#         fft_vals = rfft(windowed)
#         freqs = rfftfreq(len(frame), 1.0 / self.sr)
#         power = np.abs(fft_vals) ** 2
        
#         # Convert to dB
#         power_db = 10 * np.log10(power + 1e-10)
        
#         # Find dominant frequency
#         max_idx = np.argmax(power_db)
#         dominant_freq = freqs[max_idx]
#         dominant_power_db = power_db[max_idx]
        
#         return dominant_freq, dominant_power_db

#     def process(self, frame, transcript, is_speech, current_time=None):
#         """
#         Process audio frame for beep detection.
        
#         Args:
#             frame: Audio frame (numpy array)
#             transcript: STT transcript string
#             is_speech: Whether speech is detected in frame
#             current_time: Elapsed time in seconds
            
#         Returns:
#             (beep_detected: bool, beep_time: float or None)
#         """
#         if current_time is None:
#             self.current_time += self.frame_duration
#         else:
#             self.current_time = current_time
        
#         if self.detected:
#             return False, None
        
#         # Check if beep is expected based on transcript
#         if transcript:
#             self.beep_expected = mentions_beep(transcript)
        
#         freq, power_db = self._detect_tone_frequency(frame)
        
#         if freq is None:
#             self.count = 0
#         else:
#             # Check if dominant frequency is in beep range
#             in_range = BEEP_FREQ_MIN <= freq <= BEEP_FREQ_MAX
            
#             if in_range:
#                 if self.count == 0:
#                     self.beep_start_time = self.current_time
                
#                 self.count += 1
                
#                 # Beep confirmed: stable tone for required duration
#                 if self.count >= MIN_DURATION_FRAMES:
#                     self.detected = True
#                     beep_trigger_time = self.beep_start_time + 0.05  # +50ms as per spec
#                     return True, beep_trigger_time
#             else:
#                 self.count = 0
#                 self.beep_start_time = None
        
#         # If beep is expected, monitor silence and trigger if 3s silence without beep
#         if self.beep_expected and not is_speech:
#             if self.silence_start is None:
#                 self.silence_start = self.current_time
            
#             silence_duration = self.current_time - self.silence_start
            
#             # Timeout: beep expected but 3s silence without beep detected
#             if silence_duration >= EXPECTED_BEEP_TIMEOUT:
#                 self.detected = True
#                 return True, self.current_time
#         elif is_speech:
#             self.silence_start = None
        
#         return False, None


import numpy as np
from scipy.signal import get_window
from scipy.fft import rfft, rfftfreq
from classifier import mentions_beep

# --- Tuned constants (minimal change, high impact) ---
BEEP_FREQ_MIN = 500
BEEP_FREQ_MAX = 2000

MIN_DURATION_FRAMES = 6        # ~120 ms
FREQ_STABILITY_HZ = 30         # max allowed std deviation
SPECTRAL_RATIO_MIN = 0.35
ENERGY_FLOOR = 1e-5

EXPECTED_BEEP_TIMEOUT = 3.0


class BeepDetector:
    def __init__(self, sample_rate=16000, frame_ms=20):
        self.sr = sample_rate
        self.frame_ms = frame_ms
        self.frame_duration = frame_ms / 1000.0

        self.count = 0
        self.freq_history = []

        self.beep_start_time = None
        self.current_time = 0.0
        self.detected = False

        self.beep_expected = False
        self.silence_start = None

    def _detect_tone_frequency(self, frame):
        """
        Detect dominant frequency and spectral concentration.
        Returns (frequency, spectral_ratio) or (None, None).
        """
        if len(frame) == 0:
            return None, None

        # Energy floor check
        frame_energy = np.mean(frame ** 2)
        if frame_energy < ENERGY_FLOOR:
            return None, None

        # Windowing
        window = get_window("hann", len(frame))
        windowed = frame * window

        # FFT
        fft_vals = rfft(windowed)
        freqs = rfftfreq(len(frame), 1.0 / self.sr)
        power = np.abs(fft_vals) ** 2

        max_idx = np.argmax(power)
        dominant_freq = freqs[max_idx]

        peak_power = power[max_idx]
        total_power = np.sum(power) + 1e-10
        spectral_ratio = peak_power / total_power

        return dominant_freq, spectral_ratio

    def process(self, frame, transcript, is_speech, current_time=None):
        """
        Process audio frame for beep detection.

        Returns:
            (beep_detected: bool, beep_time: float or None)
        """
        if current_time is None:
            self.current_time += self.frame_duration
        else:
            self.current_time = current_time

        if self.detected:
            return False, None

        # Semantic hint: beep expected
        if transcript:
            self.beep_expected = mentions_beep(transcript)

        freq, spectral_ratio = self._detect_tone_frequency(frame)

        if freq is None:
            self.count = 0
            self.freq_history.clear()
        else:
            in_range = BEEP_FREQ_MIN <= freq <= BEEP_FREQ_MAX
            concentrated = spectral_ratio >= SPECTRAL_RATIO_MIN

            if in_range and concentrated:
                if self.count == 0:
                    self.beep_start_time = self.current_time

                self.count += 1
                self.freq_history.append(freq)

                if len(self.freq_history) > MIN_DURATION_FRAMES:
                    self.freq_history.pop(0)

                # Frequency stability check
                if (
                    self.count >= MIN_DURATION_FRAMES
                    and np.std(self.freq_history) <= FREQ_STABILITY_HZ
                ):
                    self.detected = True
                    return True, self.beep_start_time + 0.05

            else:
                self.count = 0
                self.freq_history.clear()
                self.beep_start_time = None

        # Expected beep fallback: silence timeout
        if self.beep_expected and not is_speech:
            if self.silence_start is None:
                self.silence_start = self.current_time

            silence_duration = self.current_time - self.silence_start

            if silence_duration >= EXPECTED_BEEP_TIMEOUT:
                self.detected = True
                return True, self.current_time

        elif is_speech:
            self.silence_start = None

        return False, None
