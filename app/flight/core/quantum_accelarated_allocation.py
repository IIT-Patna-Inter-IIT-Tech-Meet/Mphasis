import re
import math
from flight.core.Grover import Grover
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
from flight.core.allocation import BaseReallocation
from tqdm import tqdm


class QuantumReallocation(BaseReallocation):
    def __init__(
        self,
        get_pnr_fn,
        get_alt_flights_fn,
        get_cancled_fn,
        upgrade=True,
        downgrade=True,
        alpha=4,
        beta=0.3
    ) -> None:
        super().__init__(
            get_pnr_fn, get_alt_flights_fn, get_cancled_fn, upgrade, downgrade, alpha, beta
        )

    def allocate(self) -> None:
        self.used_seat = {}
        self.maximum_seat = {}

        for i in self.alt_flight:
            for j in self.alt_flight[i]["n_flights"]:
                self.used_seat[j["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j["flight_id"]] = {
                    "F": j["F"],
                    "B": j["B"],
                    "P": j["P"],
                    "E": j["E"],
                }
            for j in self.alt_flight[i]["c_flights"]:
                self.used_seat[j[0]["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j[0]["flight_id"]] = {
                    "F": j[0]["F"],
                    "B": j[0]["B"],
                    "P": j[0]["P"],
                    "E": j[0]["E"],
                }
                self.used_seat[j[1]["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j[1]["flight_id"]] = {
                    "F": j[1]["F"],
                    "B": j[1]["B"],
                    "P": j[1]["P"],
                    "E": j[1]["E"],
                }
            for j in self.alt_flight[i]["t_flights"]:
                self.used_seat[j[0]["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j[0]["flight_id"]] = {
                    "F": j[0]["F"],
                    "B": j[0]["B"],
                    "P": j[0]["P"],
                    "E": j[0]["E"],
                }
                self.used_seat[j[1]["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j[1]["flight_id"]] = {
                    "F": j[1]["F"],
                    "B": j[1]["B"],
                    "P": j[1]["P"],
                    "E": j[1]["E"],
                }
                self.used_seat[j[2]["flight_id"]] = {"F": 0, "B": 0, "P": 0, "E": 0}
                self.maximum_seat[j[2]["flight_id"]] = {
                    "F": j[2]["F"],
                    "B": j[2]["B"],
                    "P": j[2]["P"],
                    "E": j[2]["E"],
                }

        sorted_pnr = []
        for i in self.pnr:
            alloc = {}
            for j in self.pnr[i]:
                alloc = j
                alloc["flight_id"] = i
                sorted_pnr.append(alloc)
        sorted_pnr = sorted(sorted_pnr, key=lambda x: x["score"], reverse=True)

        self.allocated = {}
        sum = 0
        for i in sorted_pnr:
            self.allocated[i["pnr"]] = "NULL"

        self.tot_cost = 0

        for i in tqdm(sorted_pnr):
            #     print(i)
            f_id = i["flight_id"]
            _, _, _, list_cost, cost_id = self.obj(self.alt_flight[f_id], i)
            # print("len ",(len(list_cost)))
            if len(list_cost) == 0:
                sum += 1
                self.allocated[i["pnr"]] = ["NULL"]
                continue
            # list_cost=self.obj(self.alt_flight[f_id],i)
            #     break
            #     print(flight_id)
            #     print(cabin_id)
            ind = Grover(AerSimulator).Grover_search(list_cost)
            flight_id = cost_id[ind][0]
            cabin_id = cost_id[ind][1]
            cost = list_cost[ind]
            if len(flight_id) == 3:
                self.allocated[i["pnr"]] = [flight_id, cabin_id, cost]
                self.used_seat[flight_id[0]][cabin_id[0]] += i["pax"]
                self.used_seat[flight_id[1]][cabin_id[1]] += i["pax"]
                self.used_seat[flight_id[2]][cabin_id[2]] += i["pax"]
            elif len(flight_id) == 2:
                self.allocated[i["pnr"]] = [flight_id, cabin_id, cost]
                self.used_seat[flight_id[0]][cabin_id[0]] += i["pax"]
                self.used_seat[flight_id[1]][cabin_id[1]] += i["pax"]
            elif flight_id[0] != -1:
                self.allocated[i["pnr"]] = [flight_id, cabin_id, cost]
                self.used_seat[flight_id[0]][cabin_id[0]] += i["pax"]

        return self.allocated
