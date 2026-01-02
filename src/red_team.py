import os
import librosa
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

def simulated_attack_and_compare(protected_path, output_path):
    # 1. Load Protected Audio
    y, sr = librosa.load(protected_path, sr=None)
    
    # 2. Simulate Pre-processing (Downsampling/Filtering)
    # Most AIs downsample to 16kHz
    y_attacked = librosa.resample(y, orig_sr=sr, target_sr=16000)
    
    # 3. Calculate Loss/Damage
    print(f"Original Samples: {len(y)}")
    print(f"Attacked Samples: {len(y_attacked)}")
    
    # 4. Save the Attacked Audio
    sf.write(output_path, y_attacked, 16000)
    print(f"Attack complete: Saved '{output_path}'")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    simulated_attack_and_compare(
        os.path.join(OUTPUTS_DIR, "fully_protected.wav"),
        os.path.join(OUTPUTS_DIR, "attacked_voice_16k.wav")
    )