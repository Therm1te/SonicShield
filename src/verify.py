import os
import numpy as np
import librosa

def calculate_quality_metrics(original_path, protected_path):
    y_orig, _ = librosa.load(original_path, sr=None)
    y_prot, _ = librosa.load(protected_path, sr=None)
    
    # Ensure lengths match
    min_len = min(len(y_orig), len(y_prot))
    y_orig = y_orig[:min_len]
    y_prot = y_prot[:min_len]

    # Calculate Noise Signal
    noise = y_prot - y_orig
    
    # Power calculations
    signal_power = np.mean(y_orig ** 2)
    noise_power = np.mean(noise ** 2)
    
    # Calculate SNR (Signal-to-Noise Ratio) in Decibels
    if noise_power == 0:
        snr = float('inf')
    else:
        snr = 10 * np.log10(signal_power / noise_power)
    
    print(f"--- AUDIO QUALITY METRICS ---")
    print(f"Signal-to-Noise Ratio (SNR): {snr:.2f} dB")
    
    if snr > 40:
        print("Verdict: Excellent Quality (Imperceptible)")
    elif snr > 30:
        print("Verdict: Good Quality (Slight Artifacts)")
    else:
        print("Verdict: Poor Quality (Audible Noise)")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    calculate_quality_metrics(
        os.path.join(OUTPUTS_DIR, "input_voice.wav"), 
        os.path.join(OUTPUTS_DIR, "fully_protected.wav")
    )