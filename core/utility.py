import numpy as np
DEPTH = 8


class CustomGate:
    def __init__(self) -> None:
        self.matrix = np.zeros((2**DEPTH, 2**DEPTH), dtype = int)
        self.matrix_rev = np.zeros((2**DEPTH, 2**DEPTH), dtype = int)

    def __hotencode(self):
        pass