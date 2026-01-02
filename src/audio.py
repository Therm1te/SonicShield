import json
import os
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter

def load_quantum_bits(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    bits = np.array([int(b) for b in data["seed_bits"]])
    return 2 * bits - 1

def load_quantum_bits_raw(filepath):
    """Returns raw 0/1 bits for phase manipulation"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    bits = np.array([int(b) for b in data["seed_bits"]])
    return bits

    return bits

def butter_filter(data, cutoff, fs, btype='high', order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    if normal_cutoff >= 1.0:
        normal_cutoff = 0.999 
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    y = lfilter(b, a, data)
    return y

    return y

def generate_morse_mask(length, sr):
    """Creates an ON/OFF mask representing Morse Code 'Q' (--.-)"""
    # Timing: 100ms dot, 300ms dash
    dot_len = int(sr * 0.1) 
    dash_len = int(sr * 0.3)
    gap_len = int(sr * 0.1) 
    
    # The Pattern: Dash, Gap, Dash, Gap, Dot, Gap, Dash, Gap (Space)
    pattern = np.concatenate([
        np.ones(dash_len), np.zeros(gap_len), # Dash
        np.ones(dash_len), np.zeros(gap_len), # Dash
        np.ones(dot_len),  np.zeros(gap_len), # Dot
        np.ones(dash_len), np.zeros(gap_len), # Dash
        np.zeros(dash_len)                    # Pause between repeats
    ])
    
    # Repeat the pattern to fit the whole audio file
    repeats = int(np.ceil(length / len(pattern)))
    mask = np.tile(pattern, repeats)
    
    # Trim exactly to size
    return mask[:length]

    return mask[:length]

def apply_amplitude_protection(y, sr, key_path):
    print("Applying Amplitude Modulation...")
    
    # Prepare Quantum Noise
    q_noise_raw = load_quantum_bits(key_path)
    
    if len(q_noise_raw) < len(y):
        tile_count = int(np.ceil(len(y) / len(q_noise_raw)))
        q_noise_raw = np.tile(q_noise_raw, tile_count)
    q_noise_raw = q_noise_raw[:len(y)]

    q_noise_raw = q_noise_raw[:len(y)]

    # High frequency shield (>18kHz)
    print("  -> Generating Layer 1: Ultrasonic Shield (>18kHz)...")
    cutoff_high = 18000
    
    if sr > (cutoff_high * 2):
        noise_high = butter_filter(q_noise_raw, cutoff_high, sr, btype='high')
        
        # Imprint Digital Signature (Morse Code)
        print("  -> Imprinting Digital Signature (Morse Code)...")
        morse_mask = generate_morse_mask(len(noise_high), sr)
        noise_high = noise_high * morse_mask 
        vol_high = 0.015 
    else:
        print("  -> WARNING: Sample rate too low for 18kHz shield.")
        noise_high = np.zeros_like(y)
        vol_high = 0

        vol_high = 0

    # Low frequency noise (<4kHz)
    print("  -> Generating Layer 2: Low-Frequency Noise (<4kHz)...")
    cutoff_low = 4000
    noise_low = butter_filter(q_noise_raw, cutoff_low, sr, btype='low')
    vol_low = 0.0008 

    # Mix
    y_protected = y + (noise_high * vol_high) + (noise_low * vol_low)
    return y_protected

    y_protected = y + (noise_high * vol_high) + (noise_low * vol_low)
    return y_protected

def apply_phase_shifts(y, sr, key_path):
    print("Applying Quantum Phase Shifts...")
    
    # 1. To Frequency Domain (STFT)
    n_fft = 2048
    hop_length = 512
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    
    # Decompose into Magnitude and Phase
    magnitude, phase_angle = librosa.magphase(D)
    
    # 2. Prepare Quantum Bits for Matrix
    q_bits = load_quantum_bits_raw(key_path)
    
    # We need to cover the spectrogram matrix (Freq Bins x Time Frames)
    target_shape = phase_angle.shape
    flat_size = target_shape[0] * target_shape[1]
    
    if len(q_bits) < flat_size:
        repeats = int(np.ceil(flat_size / len(q_bits)))
        q_bits = np.tile(q_bits, repeats)
    
    # Reshape bits to match spectrogram
    q_noise_matrix = q_bits[:flat_size].reshape(target_shape)
    
    # Reshape bits to match spectrogram
    q_noise_matrix = q_bits[:flat_size].reshape(target_shape)
    
    # 3. Apply Phase Shift
    # Shift phase by 45 degrees (pi/4) wherever the quantum bit is 1.
    print(f"  -> Injecting phase offsets into {target_shape[0]}x{target_shape[1]} spectral grid...")
    shift_intensity = np.pi / 4 
    phase_shift = q_noise_matrix * shift_intensity
    
    # New Complex STFT = Magnitude * e^(i * (Original_Angle + Shift))
    new_phase_angle = np.angle(D) + phase_shift
    D_shifted = magnitude * np.exp(1j * new_phase_angle)
    
    # 4. Back to Time Domain (ISTFT)
    y_shifted = librosa.istft(D_shifted, hop_length=hop_length)
    return y_shifted

def protect_audio_pipeline(audio_path, key_path, output_path):
    # 1. Load Original
    y, sr = librosa.load(audio_path, sr=None)
    print(f"Loaded Audio: {len(y)/sr:.2f}s at {sr}Hz")

    # 2. Apply Amplitude Protection (Layers 1 & 2)
    y_amp = apply_amplitude_protection(y, sr, key_path)

    # 3. Apply Phase Shifts
    y_final = apply_phase_shifts(y_amp, sr, key_path)

    # 4. Clip and Save
    # Ensure length matches original exactly after ISTFT
    if len(y_final) > len(y):
        y_final = y_final[:len(y)]
    elif len(y_final) < len(y):
        y_final = np.pad(y_final, (0, len(y) - len(y_final)))

    y_final = np.clip(y_final, -1.0, 1.0)
    
    sf.write(output_path, y_final, sr)
    print(f"SUCCESS: Protected audio saved to: {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    
    protect_audio_pipeline(
        os.path.join(OUTPUTS_DIR, "input_voice.wav"), 
        os.path.join(OUTPUTS_DIR, "quantum_key.json"), 
        os.path.join(OUTPUTS_DIR, "fully_protected.wav")
    )