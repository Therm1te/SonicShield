import json
import os
import numpy as np
import math

def calculate_shannon_entropy(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    bits = data["seed_bits"]
    n = len(bits)
    
    # Count frequencies
    ones = bits.count('1')
    zeros = bits.count('0')
    
    p1 = ones / n
    p0 = zeros / n
    
    # Shannon Entropy Formula: H = -sum(p_i * log2(p_i))
    if p0 == 0 or p1 == 0:
        entropy = 0
    else:
        entropy = - (p1 * math.log2(p1) + p0 * math.log2(p0))
    
    print(f"--- Quantum Quality Report ---")
    print(f"Total Bits: {n}")
    print(f"Ratio: {zeros} (0s) / {ones} (1s)")
    print(f"Shannon Entropy: {entropy:.6f} / 1.0")
    
    if entropy > 0.999:
        print("VERDICT: High-Quality True Randomness (Cryptographic Grade)")
    else:
        print("VERDICT: Low Entropy (Likely bias in device)")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    calculate_shannon_entropy(os.path.join(OUTPUTS_DIR, "quantum_key.json"))