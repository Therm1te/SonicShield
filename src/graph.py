import os
import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

def compare_spectrograms(original_path, protected_path, output_image_path):
    # 1. Load Files
    print("Loading audio files...")
    y_orig, sr = librosa.load(original_path, sr=None)
    y_prot, _ = librosa.load(protected_path, sr=None)
    
    # Ensure lengths match exactly for subtraction
    min_len = min(len(y_orig), len(y_prot))
    y_orig = y_orig[:min_len]
    y_prot = y_prot[:min_len]

    # 2. Compute Spectrograms (STFT)
    # We use a larger window (n_fft) for better frequency resolution
    n_fft = 2048
    hop_length = 512
    
    D_orig = librosa.stft(y_orig, n_fft=n_fft, hop_length=hop_length)
    D_prot = librosa.stft(y_prot, n_fft=n_fft, hop_length=hop_length)
    
    # Calculate the "Difference" (The pure noise signal)
    # y_diff = y_prot - y_orig
    D_diff = librosa.stft(y_prot - y_orig, n_fft=n_fft, hop_length=hop_length)

    # Convert to decibels (dB) for visualization
    S_orig = librosa.amplitude_to_db(np.abs(D_orig), ref=np.max)
    S_prot = librosa.amplitude_to_db(np.abs(D_prot), ref=np.max)
    S_diff = librosa.amplitude_to_db(np.abs(D_diff), ref=np.max)

    # 3. Plotting
    fig, ax = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
    # --- Plot 1: Original ---
    img1 = librosa.display.specshow(S_orig, sr=sr, x_axis='time', y_axis='linear', ax=ax[0], cmap='inferno')
    ax[0].set_title('1. Original Audio (Clean)', fontsize=14, fontweight='bold')
    ax[0].set_ylabel('Frequency (Hz)')
    ax[0].text(0.5, 19000, 'Empty Space (Vulnerable)', color='white', ha='left', fontsize=10, backgroundcolor='black')

    # --- Plot 2: Protected ---
    img2 = librosa.display.specshow(S_prot, sr=sr, x_axis='time', y_axis='linear', ax=ax[1], cmap='inferno')
    ax[1].set_title('2. Dual-Layer Protected Audio', fontsize=14, fontweight='bold')
    ax[1].set_ylabel('Frequency (Hz)')
    
    # Highlight Layer 1
    ax[1].axhline(y=18000, color='cyan', linestyle='--')
    ax[1].text(0.5, 18500, 'LAYER 1: >18kHz Quantum Shield', color='cyan', fontweight='bold', ha='left')

    # --- Plot 3: The "X-Ray" (Difference) ---
    # This proves Layer 2 exists, even if it's quiet!
    img3 = librosa.display.specshow(S_diff, sr=sr, x_axis='time', y_axis='linear', ax=ax[2], cmap='magma')
    ax[2].set_title('3. X-Ray View (The Injected Noise Only)', fontsize=14, fontweight='bold')
    ax[2].set_ylabel('Frequency (Hz)')
    ax[2].set_xlabel('Time (s)')

    # Highlight Both Layers clearly here
    ax[2].axhline(y=18000, color='cyan', linestyle='--', alpha=0.7)
    ax[2].text(0.2, 19000, 'LAYER 1: High Amplitude', color='cyan', fontweight='bold')
    
    ax[2].axhline(y=4000, color='yellow', linestyle='--', alpha=0.7)
    ax[2].text(0.2, 2000, 'LAYER 2: Low Amplitude (<4kHz Grit)', color='yellow', fontweight='bold')
    
    # Add colorbars
    for i, img in enumerate([img1, img2, img3]):
        fig.colorbar(img, ax=ax[i], format='%+2.0f dB')

    plt.tight_layout()
    plt.savefig(output_image_path)
    print(f"Graph saved as '{output_image_path}'")
    plt.show()

if __name__ == "__main__":
    # Ensure you use the file generated from the 'Dual-Layer' step
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')
    
    compare_spectrograms(
        os.path.join(OUTPUTS_DIR, "input_voice.wav"), 
        os.path.join(OUTPUTS_DIR, "fully_protected.wav"),
        os.path.join(IMAGES_DIR, "final_comparison_proof.png")
    )