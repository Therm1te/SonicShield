import os
import sys
import argparse
from src.seed import generate_quantum_seed
from src.audio import protect_audio_pipeline
from src.graph import compare_spectrograms
from src.verify import calculate_quality_metrics
from src.decode import decode_watermark
from src.red_team import simulated_attack_and_compare
from src.vis_advanced import plot_advanced_metrics

def main():
    parser = argparse.ArgumentParser(description="The Sonic Shield: Quantum Audio Defense CLI")
    parser.add_argument("-i", "--input", required=True, help="Path to input .wav file")
    parser.add_argument("-k", "--key", default="outputs/quantum_key.json", help="Path to Quantum Key")
    parser.add_argument("--strength", type=float, default=0.015, help="Injection strength (0.01 - 0.05)")
    parser.add_argument("--attack", action="store_true", help="Run simulated AI attack verification")
    
    args = parser.parse_args()

    # Setup Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(base_dir, 'outputs')
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # File Checks
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found.")
        sys.exit(1)

    filename = os.path.basename(args.input).split('.')[0]
    protected_wav = os.path.join(outputs_dir, f"{filename}_protected.wav")
    attacked_wav = os.path.join(outputs_dir, f"{filename}_attacked.wav")
    
    print(f"Starting Sonic Shield Protocol for: {args.input}")

    # Quantum Key Check
    if not os.path.exists(args.key):
        print("Quantum Key not found. Generating new key...")
        try:
            generate_quantum_seed(args.key)
        except Exception as e:
            print(f"Error: Quantum generation failed: {e}")
            sys.exit(1)
    
    # Protection
    print(f"Applying Audio Protection (Strength: {args.strength})...")
    # Note: 'strength' can be passed to audio function if needed
    protect_audio_pipeline(args.input, args.key, protected_wav)

    # Verify Ownership
    print("Verifying Watermark Signature...")
    decode_watermark(protected_wav)

    # Metrics
    print("Calculating Signal Fidelity...")
    calculate_quality_metrics(args.input, protected_wav)

    # Visuals
    print("Generating Visualizations...")
    plot_advanced_metrics(args.input, protected_wav, images_dir)
    compare_spectrograms(args.input, protected_wav, os.path.join(images_dir, "spectrogram_proof.png"))

    # Optional Attack Simulation
    if args.attack:
        print("Running Attack Simulation...")
        simulated_attack_and_compare(protected_wav, attacked_wav)

    print(f"\nProcessing complete. Artifacts saved in {outputs_dir} and {images_dir}.")

if __name__ == "__main__":
    main()