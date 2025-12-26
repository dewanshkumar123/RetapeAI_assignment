import os
import numpy as np
import soundfile as sf
import resampy
import matplotlib.pyplot as plt
from scipy.signal import spectrogram, get_window
from scipy.fft import rfft, rfftfreq

TARGET_SR = 16000

def create_plots(audio_file):
    """
    Analyze audio file and create plots for frequency, amplitude, and spectrogram.
    
    Args:
        audio_file: Path to .wav file to analyze
    """
    
    # Load audio
    print(f"Loading {audio_file}...")
    data, sr = sf.read(audio_file)
    
    # Convert stereo to mono if needed
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Resample if needed
    if sr != TARGET_SR:
        print(f"Resampling from {sr} to {TARGET_SR}Hz...")
        data = resampy.resample(data, sr, TARGET_SR)
        sr = TARGET_SR
    
    # Create output directory
    filename = os.path.splitext(os.path.basename(audio_file))[0]
    output_dir = f"plots_{filename}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating plots in {output_dir}/...")
    
    # Time axis
    time = np.arange(len(data)) / sr
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Plot 1: Waveform (Amplitude vs Time)
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(time, data, linewidth=0.5)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Waveform - Amplitude vs Time')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Spectrogram
    ax2 = plt.subplot(3, 2, 2)
    f, t, Sxx = spectrogram(data, sr, nperseg=2048, noverlap=1024)
    im = ax2.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax2.set_ylabel('Frequency (Hz)')
    ax2.set_xlabel('Time (s)')
    ax2.set_title('Spectrogram - Frequency vs Time vs Power')
    ax2.set_ylim([0, 4000])  # Focus on voice frequencies
    plt.colorbar(im, ax=ax2, label='Power (dB)')
    
    # Plot 3: Full Frequency Spectrum (FFT of entire signal)
    ax3 = plt.subplot(3, 2, 3)
    fft_vals = rfft(data)
    freqs = rfftfreq(len(data), 1.0 / sr)
    power = np.abs(fft_vals) ** 2
    power_db = 10 * np.log10(power + 1e-10)
    ax3.semilogy(freqs, power_db, linewidth=0.5)
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Power (dB)')
    ax3.set_title('Full Frequency Spectrum')
    ax3.set_xlim([0, 4000])
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Beep Detection Region (900-1600 Hz focus)
    ax4 = plt.subplot(3, 2, 4)
    beep_mask = (freqs >= 900) & (freqs <= 1600)
    ax4.semilogy(freqs[beep_mask], power_db[beep_mask], 'r-', linewidth=1)
    ax4.axvline(x=900, color='g', linestyle='--', label='Beep Range Min')
    ax4.axvline(x=1600, color='b', linestyle='--', label='Beep Range Max')
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Power (dB)')
    ax4.set_title('Beep Detection Region (900-1600 Hz)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Spectrogram zoomed to beep region
    ax5 = plt.subplot(3, 2, 5)
    im2 = ax5.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax5.set_ylabel('Frequency (Hz)')
    ax5.set_xlabel('Time (s)')
    ax5.set_title('Spectrogram - Beep Region (900-1600 Hz)')
    ax5.set_ylim([900, 1600])
    plt.colorbar(im2, ax=ax5, label='Power (dB)')
    
    # Plot 6: Frame-by-frame dominant frequency
    ax6 = plt.subplot(3, 2, 6)
    frame_size = int(TARGET_SR * 0.020)  # 20ms frames
    frame_times = []
    dominant_freqs = []
    
    for i in range(0, len(data) - frame_size, frame_size):
        frame = data[i:i + frame_size]
        window = get_window('hann', len(frame))
        windowed = frame * window
        
        fft_frame = rfft(windowed)
        freqs_frame = rfftfreq(len(frame), 1.0 / TARGET_SR)
        power_frame = np.abs(fft_frame) ** 2
        
        max_idx = np.argmax(power_frame)
        dominant_freq = freqs_frame[max_idx]
        
        frame_times.append(i / TARGET_SR)
        dominant_freqs.append(dominant_freq)
    
    ax6.plot(frame_times, dominant_freqs, linewidth=1, marker='o', markersize=2)
    ax6.axhline(y=900, color='g', linestyle='--', label='Beep Min', alpha=0.7)
    ax6.axhline(y=1600, color='b', linestyle='--', label='Beep Max', alpha=0.7)
    ax6.set_xlabel('Time (s)')
    ax6.set_ylabel('Dominant Frequency (Hz)')
    ax6.set_title('Dominant Frequency per 20ms Frame')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plots
    plot_file = os.path.join(output_dir, f'{filename}_analysis.png')
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {plot_file}")
    
    # Also save individual plots for closer inspection
    
    # Save spectrogram only
    fig_spec = plt.figure(figsize=(14, 6))
    f, t, Sxx = spectrogram(data, sr, nperseg=2048, noverlap=1024)
    plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title('Spectrogram - Full Range')
    plt.ylim([0, 8000])
    plt.colorbar(label='Power (dB)')
    spec_file = os.path.join(output_dir, f'{filename}_spectrogram_full.png')
    plt.savefig(spec_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {spec_file}")
    plt.close(fig_spec)
    
    # Save beep region spectrogram
    fig_beep = plt.figure(figsize=(14, 6))
    plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title('Spectrogram - Beep Region (900-1600 Hz)')
    plt.ylim([900, 1600])
    plt.colorbar(label='Power (dB)')
    beep_file = os.path.join(output_dir, f'{filename}_spectrogram_beep.png')
    plt.savefig(beep_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {beep_file}")
    plt.close(fig_beep)
    
    # Save waveform only
    fig_wave = plt.figure(figsize=(14, 4))
    plt.plot(time, data, linewidth=0.5)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Waveform')
    plt.grid(True, alpha=0.3)
    wave_file = os.path.join(output_dir, f'{filename}_waveform.png')
    plt.savefig(wave_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {wave_file}")
    plt.close(fig_wave)
    
    plt.close(fig)
    
    # Print audio statistics
    print(f"\n{'='*50}")
    print(f"Audio Statistics for: {filename}")
    print(f"{'='*50}")
    print(f"Sample Rate: {sr} Hz")
    print(f"Duration: {len(data) / sr:.2f} seconds")
    print(f"Total Samples: {len(data)}")
    print(f"Amplitude Range: [{data.min():.4f}, {data.max():.4f}]")
    print(f"RMS Level: {np.sqrt(np.mean(data**2)):.4f}")
    print(f"Peak Frequency: {freqs[np.argmax(power_db)]:.2f} Hz")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # Change this path to the audio file you want to analyze
    audio_file = "voicemails/vm2.wav"
    
    if not os.path.exists(audio_file):
        print(f"Error: File '{audio_file}' not found!")
        exit(1)
    
    create_plots(audio_file)
    print(f"Analysis complete! Check the plots_* folder for visualizations.")
