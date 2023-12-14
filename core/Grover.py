from P2Q import P2Q
from qiskit import QuantumCircuit
import numpy as np
import math
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit as qc
from qiskit import QuantumRegister as qr
from qiskit import execute
from matplotlib.pyplot import show, subplots, xticks, yticks
from qiskit_aer import Aer
from math import pi, sqrt
from heapq import nlargest

class Grover:
    
    def __init__(self, simulator) -> None:
        self.simulator = simulator
        self.circuit = None
        self.shots = 100
        
    def Grover_search(self,states):
  
        instance=P2Q(self.simulator)
        instance.build_circuit(states)
        painted_target = instance.result()

        N: int = math.ceil(np.log2(len(states)))                              
        SEARCH_VALUES: set[int] = {int(painted_target,2)} 
        SHOTS: int = 100                       
        FONTSIZE: int = 10                      

        TARGETS: set[str] = {f"{s:0{N}b}" for s in SEARCH_VALUES}  
        QUBITS: qr = qr(N, "qubit")                                

        def print_circuit(circuit: qc, name: str = None) -> None:
            print(f"\n{name}:" if name else "")
            print(f"{circuit}")

        def oracle(targets: set[str] = TARGETS, name: str = "Oracle", display_oracle: bool = True) -> qc:
            # Create N-qubit quantum circuit for oracle
            oracle = qc(QUBITS, name = name)

            for target in targets:
                # Reverse target state since Qiskit uses little-endian for qubit ordering
                target = target[::-1]
                
                # Flip zero qubits in target
                for i in range(N):
                    if target[i] == "0":
                        oracle.x(i)                    # Pauli-X gate

                # Simulate (N - 1)-control Z gate
                oracle.h(N - 1)                        # Hadamard gate
                oracle.mcx(list(range(N - 1)), N - 1)  # (N - 1)-control Toffoli gate
                oracle.h(N - 1)                        # Hadamard gate

                # Flip back to original state
                for i in range(N):
                    if target[i] == "0":
                        oracle.x(i)                    # Pauli-X gate

            # Display oracle, if applicable
            # if display_oracle:
            #     print_circuit(oracle, "ORACLE")

            return oracle

        def diffuser(name: str = "Diffuser", display_diffuser: bool = True) -> qc:
            # Create N-qubit quantum circuit for diffuser
            diffuser = qc(QUBITS, name = name)
            
            diffuser.h(QUBITS)                          # Hadamard gate
            diffuser.append(oracle({"0" * N}), QUBITS)  # Oracle with all zero target state
            diffuser.h(QUBITS)                          # Hadamard gate

            # Display diffuser, if applicable
            # if display_diffuser:
            #     print_circuit(diffuser, "DIFFUSER")
            
            return diffuser

        def grover(oracle: qc = oracle(), diffuser: qc = diffuser(), name: str = "Grover Circuit", display_grover: bool = True) -> qc:
            # Create N-qubit quantum circuit for Grover's algorithm
            grover = qc(QUBITS, name = name)
            
            # Intialize qubits with Hadamard gate (i.e. uniform superposition)
            grover.h(QUBITS)
            
            # Apply barrier to separate steps
            grover.barrier()
            
            # Apply oracle and diffuser (i.e. Grover operator) optimal number of times
            for _ in range(int((pi / 4) * sqrt((2 ** N) / len(TARGETS)))):
                grover.append(oracle, QUBITS)
                grover.append(diffuser, QUBITS)
            
            # Measure all qubits once finished
            grover.measure_all()

            # Display grover circuit, if applicable
            # if display_grover:
            #     print_circuit(grover, "GROVER CIRCUIT")
            
            return grover

        def outcome(winners: dict[str, int]) -> None:
            print("\nWINNER(S):")
            print(f"Binary = {[*winners]}\nDecimal = {[int(winner, 2) for winner in [*winners]]}\n")
                
            print("TARGET(S):")
            print(f"Binary = {TARGETS}\nDecimal = {SEARCH_VALUES}\n")
            
            print(f"Target(s) found with {sum(winners.values()) / SHOTS:.2%} accuracy!\n"
                if all(winner in TARGETS for winner in [*winners])
                else "Target(s) not found...\n")

        def display_results(results: dict[str, int], combine_other_states: bool = True) -> None:
            # State(s) with highest count and their frequencies
            winners = {winner : results.get(winner) for winner in nlargest(len(TARGETS), results, key = results.get)}

            # Print outcome
            outcome(winners)

            # X-axis and y-axis value(s) for winners, respectively
            winners_x_axis = [str(winner) for winner in [*winners]]
            winners_y_axis = [*winners.values()]

            # All other states (i.e. non-winners) and their frequencies
            others = {state : frequency for state, frequency in results.items() if state not in winners}

            # X-axis and y-axis value(s) for all other states, respectively
            other_states_x_axis = "Others" if combine_other_states else [*others]
            other_states_y_axis = [sum([*others.values()])] if combine_other_states else [*others.values()]

            # Create histogram for simulation results
            figure, axes = subplots(num = "Grover's Algorithm — Results", layout = "constrained")
            axes.bar(winners_x_axis, winners_y_axis, color = "green", label = "Target")
            axes.bar(other_states_x_axis, other_states_y_axis, color = "red", label = "Non-target")
            axes.legend(fontsize = FONTSIZE)
            axes.grid(axis = "y", ls = "dashed")
            axes.set_axisbelow(True)

            # Set histogram title, x-axis title, and y-axis title respectively
            axes.set_title(f"Outcome of {SHOTS} Simulations", fontsize = int(FONTSIZE * 1.45))
            axes.set_xlabel("States (Qubits)", fontsize = int(FONTSIZE * 1.3))
            axes.set_ylabel("Frequency", fontsize = int(FONTSIZE * 1.3))

            # Set font properties for x-axis and y-axis labels respectively
            xticks(fontsize = FONTSIZE, family = "monospace", rotation = 0 if combine_other_states else 70)
            yticks(fontsize = FONTSIZE, family = "monospace")
            
            # Set properties for annotations displaying frequency above each bar
            annotation = axes.annotate("",
                                    xy = (0, 0),
                                    xytext = (5, 5),
                                    xycoords = "data",
                                    textcoords = "offset pixels",
                                    ha = "center",
                                    va = "bottom",
                                    family = "monospace",
                                    weight = "bold",
                                    fontsize = FONTSIZE,
                                    bbox = dict(facecolor = "white", alpha = 0.4, edgecolor = "None", pad = 0)
                                    )
            
            def hover(event) -> None:
                visibility = annotation.get_visible()
                if event.inaxes == axes:
                    for bars in axes.containers:
                        for bar in bars:
                            cont, _ = bar.contains(event)
                            if cont:
                                x, y = bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height()
                                annotation.xy = (x, y)
                                annotation.set_text(y)
                                annotation.set_visible(True)
                                figure.canvas.draw_idle()
                                return
                if visibility:
                    annotation.set_visible(False)
                    figure.canvas.draw_idle()
                
            # Display histogram
            id = figure.canvas.mpl_connect("motion_notify_event", hover)
            show()
            figure.canvas.mpl_disconnect(id)

        # Generate quantum circuit for Grover's algorithm 
        grover_circuit = grover()
        # Simulate Grover's algorithm with grover_circuit SHOTS times and get results
        results = execute(grover_circuit, backend = Aer.get_backend("qasm_simulator"), shots = SHOTS).result()
        
        # Get each state's frequency and display simulation results
        # display_results(results.get_counts())
        # print(grover_circuit)
        exp_counts = results.get_counts()
        return int(max(exp_counts, key=exp_counts.get),2)
