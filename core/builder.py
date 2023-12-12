import math
import argparse
# import matplotlib
# matplotlib.use('GTK3Agg')

from qiskit import QuantumCircuit, execute, QuantumRegister, Aer, BasicAer, transpile
from qiskit.tools.visualization import plot_histogram
from qiskit.extensions import UnitaryGate
from qiskit.circuit.library.standard_gates import XGate

from utility import CustomGate


class UtilityGates:
    def __init__(self, n) -> None:
        self.custom_gate = CustomGate(n)
        self.Uf = UnitaryGate(self.custom_gate.matrix, label="Uf")
        self.Uf_rev = UnitaryGate(self.custom_gate.matrix_rev, label="Uf_rev")

    @staticmethod
    def _n_hadamard(n):
        # return a n qubit hadamard gate
        circuit = QuantumCircuit(QuantumRegister(n, "q"))
        circuit.h(range(0, n))
        circuit.name = "Hn"
        # print(circuit)
        return circuit
    
    @staticmethod
    def _n_diffuser(n):
        circuit = QuantumCircuit(QuantumRegister(n, "q"))
        circuit.append(UtilityGates._n_hadamard(n-1), range(0, n-1))

        # apply anti control
        for i in range(0, n-1):
            circuit.x(i)

        circuit.append(XGate().control(n-1), range(0, n))

        # apply anti control
        for i in range(0, n-1):
            circuit.x(i)

        circuit.append(UtilityGates._n_hadamard(n-1), range(0, n-1))
        circuit.name = "Dn"
        # print(circuit)
        return circuit

    
    @staticmethod
    def _n_toffoli(n, query):
        _bitstring_query = "{0:08b}".format(query)
        _bitstring_query = _bitstring_query[::-1][:n-1]
        circuit = QuantumCircuit(QuantumRegister(n-1, "q"), QuantumRegister(1, "y"))

        for i in range(0, n-1):
            if _bitstring_query[i] == "0":
                circuit.x(i)
        ncx = XGate().control(n-1)
        circuit.append(ncx, range(0, n))
        for i in range(0, n-1):
            if _bitstring_query[i] == "0":
                circuit.x(i)
        circuit.name = "nCX"
        # print(circuit)
        return circuit
        


class GroversSearch:
    def __init__(self, n) -> None:
        self.n = n
        self.circuit = None
        self.itretion = int(math.pi/4 * math.sqrt(2**n))
        self.utitlity = UtilityGates(n)
        self._build_circuit()

        self.simulator = Aer.get_backend('qasm_simulator')

    def _build_circuit(self, query = 0):
        self.query = query
        self.circuit = QuantumCircuit(QuantumRegister(self.n, "q"), QuantumRegister(1, "y"))
        # initialization
        self.circuit.append(UtilityGates._n_hadamard(self.n), range(0, self.n))
        self.circuit.x(self.n)
        self.circuit.h(self.n)

        for _ in range(self.itretion):
            # oracle
            self.circuit.append(self.utitlity.Uf, range(0, self.n))
            self.circuit.append(self.utitlity._n_toffoli(self.n + 1, query), range(0, self.n + 1))
            self.circuit.append(self.utitlity.Uf_rev, range(0, self.n))

            # defuser
            self.circuit.append(self.utitlity._n_diffuser(self.n + 1), range(0, self.n + 1))

        self.circuit.measure_all()

    def run(self):
        compiled_circuit = transpile(self.circuit, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=1000)
        result = job.result()
        counts = result.get_counts(self.circuit)
        print(counts)

        # get 2 most frequent results
        max1 = max(counts, key=counts.get)
        print(f"Query: {self.query}, Result: {int(max1[1:],2)}")


    def show(self):
        self.circuit.draw("mpl")
        print(self.circuit)