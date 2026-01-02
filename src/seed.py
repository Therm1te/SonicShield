import json
import os
from dotenv import load_dotenv
import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()
api_key = os.getenv("IBM_TOKEN") 

def generate_quantum_seed(output_path):
    # Authenticate
    QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token=api_key, overwrite=True)
    service = QiskitRuntimeService()

    # Select Backend with sufficient qubits
    backend = service.least_busy(min_num_qubits=127)
    print(f"Targeting Backend: {backend.name}")

    # Build Entropy Circuit (Hadamard gates on all qubits)
    num_qubits = 127
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    qc.measure_all()

    # Transpile
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuit = pm.run(qc)

    # Execute Batch (4096 shots)
    sampler = Sampler(backend)
    job = sampler.run([isa_circuit], shots=4096)
    
    print(f"Job submitted: {job.job_id()} - Waiting for completion...")
    result = job.result()
    
    # Extract Data
    pub_result = result[0]
    bit_array = pub_result.data.meas.get_bitstrings()
    
    full_bitstring = "".join(bit_array)
    
    print(f"Entropy Generated: {len(full_bitstring)} bits")

    with open(output_path, "w") as f:
        json.dump({"seed_bits": full_bitstring}, f)
        
    print(f"Quantum Seed saved to {output_path}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
    generate_quantum_seed(os.path.join(OUTPUTS_DIR, "quantum_key.json"))