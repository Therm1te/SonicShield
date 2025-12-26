import json
import os
from dotenv import load_dotenv
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()
api_key = os.getenv("IBM_TOKEN") 

def generate_quantum_seed():
    # 1. Authenticate (Ensure your API token is saved locally or pass it here)
    QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token=api_key, overwrite=True)
    service = QiskitRuntimeService()

    # 2. Select a Backend
    # We choose the least busy backend with at least 127 qubits to maximize throughput
    backend = service.least_busy(min_num_qubits=127)
    print(f"Targeting Backend: {backend.name}")

    # 3. Build the Entropy Circuit
    # We apply Hadamard gates to all qubits to put them in superposition (|0> + |1>) / sqrt(2)
    # Upon measurement, this collapses to 0 or 1 with true randomness.
    num_qubits = 127
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    qc.measure_all()

    # 4. Transpile for the hardware
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)

    # 5. Execute - The "Batch" Strategy
    # We ask for 4096 shots. 
    # Total bits = 127 qubits * 4096 shots = ~520,000 bits (approx 65KB of entropy)
    # This costs only a few seconds of runtime.
    sampler = Sampler(backend)
    job = sampler.run([isa_circuit], shots=4096)
    
    print(f"Job submitted: {job.job_id()} - Waiting for completion...")
    result = job.result()
    
    # 6. Extract Data
    # SamplerV2 returns BitArrays. We need to flatten this into a single bitstring.
    pub_result = result[0]
    # Get the counts or raw bitstreams. implementation details vary slightly by version,
    # but accessing the BitArray is standard for V2.
    bit_array = pub_result.data.meas.get_bitstrings()
    
    # Flatten list of strings into one massive string
    full_bitstring = "".join(bit_array)
    
    print(f"entropy_length: {len(full_bitstring)} bits")

    # 7. Save to Local Artifact
    with open("quantum_key.json", "w") as f:
        json.dump({"seed_bits": full_bitstring}, f)
        
    print("Quantum Seed successfully saved to quantum_key.json")

if __name__ == "__main__":
    generate_quantum_seed()