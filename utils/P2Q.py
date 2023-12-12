from qiskit import QuantumCircuit
import numpy as np
import math
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

class P2Q:    
    def __init__(self, simulator) -> None:
        self.simulator = simulator
        self.circuit = None
        self.shots = 1000
    
    def __build_circuit(self, states):
        # Deal with improper number of passed states
        nq = np.log2(len(states))
        if not(nq.is_integer()):
            n = 2**(math.ceil(nq)) - math.floor(nq)
            for i in n:
                states.append(0)
        # Calculate normalizatrion factor
        sm = 0
        for x in states:
            sm += x**2
        norm = sm**0.5
        # assign circuit to self.circuit
        self.circuit = QuantumCircuit(np.log2(len(states)))      
        self.circuit.prepare_state(states/norm, [i for i in len(states)])
        self.circuit.measure_all()
        self.circuit = transpile(self.circuit, self.simulator)
    
    def result(self):
        job = self.simulator.run(self.circuit, shots=self.shots, dynamic=True)

        # Get the results and display them
        exp_result = job.result()
        exp_counts = exp_result.get_counts()
        # plot_histogram(exp_counts)
        return max(exp_counts, key=exp_counts.get)