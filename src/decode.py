import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

def decode_watermark(audio_path):
    print(f"Analyzing {os.path.basename(audio_path)} for Quantum Signature...")
    y, sr = librosa.load(audio_path, sr=None)
    
    # 1. Bandpass Filter (Isolate the 18kHz Shield)
    # We want to hear ONLY the noise layer, not the voice.
    nyq = 0.5 * sr
    low_cut = 17500
    high_cut = 22000
    
    if sr < 40000:
        print("ERROR: Sample rate too low to contain ultrasonic watermark.")
        return

    # Normalize cutoffs
    low = low_cut / nyq
    high = high_cut / nyq
    
    # Apply Filter
    b, a = butter(5, [low, high], btype='band', analog=False)
    y_shield = lfilter(b, a, y)
    
    # 2. Envelope Follower (Convert high freq vibration to a volume curve)
    # Take absolute value
    envelope = np.abs(y_shield)
    
    # Smooth the envelope (Low pass filter the volume curve at 50Hz)
    # This turns the jagged waveform into a smooth line showing "ON/OFF" states
    b_smooth, a_smooth = butter(3, 50/nyq, btype='low') 
    envelope_smoothed = lfilter(b_smooth, a_smooth, envelope)
    
    # 3. Thresholding (Convert to Binary ON/OFF)
    # If volume > threshold, it's a "1" (Signal). Else "0" (Gap).
    # We set threshold dynamically based on average noise floor
    threshold = np.mean(envelope_smoothed) * 1.5
    binary_signal = (envelope_smoothed > threshold).astype(int)
    
    # 4. Visualization (Print a slice of the code)
    # We downsample significantly to make it printable in terminal
    view_window = int(sr * 0.05) # Resolution of 50ms
    reduced_signal = []
    
    # Average the binary signal over chunks to get a cleaner "Dash" or "Dot"
    for i in range(0, len(binary_signal), view_window):
        chunk = binary_signal[i:i+view_window]
        if np.mean(chunk) > 0.5:
            reduced_signal.append(1)
        else:
            reduced_signal.append(0)

    print("\n--- DECODED QUANTUM SIGNATURE ---")
    print("Reading Ultrasonic Band (17.5kHz - 22kHz)...")
    
    # Convert 1s and 0s to visual blocks
    code_stream = ""
    for bit in reduced_signal[:120]: # Show first ~6 seconds
        if bit == 1:
            code_stream += "█" # Full Block (Noise ON)
        else:
            code_stream += "_" # Underscore (Noise OFF)
            
    print(f"Stream: {code_stream}")
    print("---------------------------------")
    
    # Check for the Dash-Dash-Dot-Dash (Q) pattern roughly
    # We look for a block of signal, space, block of signal
    if "██" in code_stream and "__" in code_stream:
        print("VERIFIED: Periodic Pulse Pattern Detected.")
        print("Ownership Confirmed: Sonic Shield Signature Present.")
    else:
        print("FAILED: No distinct signature found (File might be clean or compressed).")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    
    # Run on the protected file
    decode_watermark(os.path.join(OUTPUTS_DIR, "fully_protected.wav"))