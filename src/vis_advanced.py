import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

def plot_advanced_metrics(original_path, protected_path, output_dir):
    print("Generating Advanced Scientific Visuals...")
    
    # Load Files
    y_orig, sr = librosa.load(original_path, sr=None)
    y_prot, _ = librosa.load(protected_path, sr=None)
    
    # Ensure lengths match
    min_len = min(len(y_orig), len(y_prot))
    y_orig = y_orig[:min_len]
    y_prot = y_prot[:min_len]

    # --- VIZ 1: Power Spectral Density ---
    plt.figure(figsize=(12, 6))
    plt.title("Power Spectral Density")
    plt.psd(y_orig, NFFT=2048, Fs=sr, label='Original Voice', color='blue', alpha=0.7)
    plt.psd(y_prot, NFFT=2048, Fs=sr, label='Protected Voice', color='red', alpha=0.5)
    plt.legend()
    plt.xlim(0, 22000) # Show full range
    plt.tight_layout()
    plt.savefig(f"{output_dir}/viz_psd_comparison.png")
    print(f"  -> Saved {output_dir}/viz_psd_comparison.png")
    plt.close()

    # --- VIZ 2: Phase Constellation ---
    # We look at a specific frequency bin (e.g., 1000Hz) over time
    n_fft = 2048
    bin_idx = 100 # Approx 1000-2000Hz range depending on SR
    
    D_orig = librosa.stft(y_orig, n_fft=n_fft)
    D_prot = librosa.stft(y_prot, n_fft=n_fft)
    
    # Extract Complex Numbers for that frequency bin
    z_orig = D_orig[bin_idx, :]
    z_prot = D_prot[bin_idx, :]

    plt.figure(figsize=(8, 8))
    plt.title(f"Phase Scatter Plot (Freq Bin {bin_idx})")
    plt.axhline(0, color='gray', linewidth=0.5)
    plt.axvline(0, color='gray', linewidth=0.5)
    
    # Plot Original (Blue Dots)
    plt.scatter(z_orig.real, z_orig.imag, s=5, c='blue', alpha=0.5, label='Original Phase')
    
    # Plot Protected (Red Dots)
    plt.scatter(z_prot.real, z_prot.imag, s=5, c='red', alpha=0.5, label='Protected Phase')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/viz_phase_constellation.png")
    print(f"  -> Saved {output_dir}/viz_phase_constellation.png")
    plt.close()

    # --- VIZ 3: Chromagram Difference ---
    # Checks that pitch features are preserved
    chroma_orig = librosa.feature.chroma_stft(y=y_orig, sr=sr)
    chroma_prot = librosa.feature.chroma_stft(y=y_prot, sr=sr)
    
    fig, ax = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(12, 8))
    
    librosa.display.specshow(chroma_orig, y_axis='chroma', x_axis='time', ax=ax[0])
    ax[0].set_title('Original Chromagram')
    
    librosa.display.specshow(chroma_prot, y_axis='chroma', x_axis='time', ax=ax[1])
    ax[1].set_title('Protected Chromagram')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/viz_chroma_proof.png")
    print(f"  -> Saved {output_dir}/viz_chroma_proof.png")
    plt.close()

if __name__ == "__main__":
    # Test run
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')
    
    plot_advanced_metrics(
        os.path.join(OUTPUTS_DIR, "input_voice.wav"), 
        os.path.join(OUTPUTS_DIR, "fully_protected.wav"),
        IMAGES_DIR
    )