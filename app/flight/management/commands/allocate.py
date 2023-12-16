import ast
import time
import datetime
import pandas as pd
from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import *
from app.config import load_settings
from flight.core.allocation import PnrReallocation
from flight.core.quantum_accelarated_allocation import QuantumReallocation
from flight.utils import (
    util_flight_ranking,
    util_pnr_ranking,
    cancelled_flight,
    CLASS_CABIN_MAPPING,
)

CABIN_CLASS_MAPPING = {}
for key, value in CLASS_CABIN_MAPPING.items():
    for v in value:
        CABIN_CLASS_MAPPING[v] = key
DIVIDER = "----------------"

# print(CABIN_CLASS_MAPPING)


class Command(BaseCommand):
    help = "Allocates alternate flights for cancelled flights"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--config",
            type=str,
            default="settings.yml",
        )

        parser.add_argument(
            "--save",
            type=str,
            default="result.csv",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def wrapper_flight_ranking(self):
        # def util_flight_ranking(flight_id, max_hop=2, use_inventory=False, use_cabin_only=True, neighboring_search=True):
        def callable_function(flight_id):
            return util_flight_ranking(
                flight_id,
                max_hop=self.config["search"]["max_hop"],
                use_inventory=self.config["search"]["use_inventory"],
                use_cabin_only=self.config["search"]["use_cabin_only"],
                neighboring_search=self.config["search"]["neighboring_search"],
            )

        return callable_function

    def savefile(self, filename="result.csv"):
        # result <dict> format :
        #   pnr : [list of inv-id]/single_inv_id, [list of class]/single_class, score
        # save self.data in csv file
        self.filename = filename
        self.df = pd.DataFrame(self.data, columns= [
                "pnr",
                "pax",
                "pnr_score",
                "canclled_flight",
                "canclled_class",
                "canclled_flight_departure",
                "canclled_flight_arrival",
                "canclled_src",
                "canclled_dst",
                "allocated_src",
                "allocated_dst",
                "allocated_flights",
                "allocated_flights_departure",
                "allocated_flights_arrival",
                "allocated_classes",
                "flight_time",
                "allocated_flights_score",
            ]
        )
        self.df.to_csv(filename, index=False)
        print("Result saved result in file : ", filename)

    def generate_report(self):
        # open a file to save report
        f = open(f"{self.filename.split('.')[0]}.txt", "w")
        def printf(*args):
            f.write(" ".join([str(x) for x in args]) + "\n")
            print(*args)

        df = pd.read_csv(self.filename)
        ## STATIC REPOPRT
        mean_score = df["pnr_score"].mean()
        std_dev_score = df["pnr_score"].std()
        printf("PNR Score Stats")
        printf("Mean PNR Score: ", mean_score)
        printf("Std Dev. PNR Score: ", std_dev_score)
        printf("Max PNR Score: ", df["pnr_score"].max())
        printf("Min PNR Score: ", df["pnr_score"].min())
        printf(DIVIDER)

        mean_score = df["allocated_flights_score"].mean()
        std_dev_score = df["allocated_flights_score"].std()
        printf("PNR-FLIGHT Score Stats")
        printf("Mean PNR-FLIGHT Score: ", mean_score)
        printf("Std Dev. PNR-FLIGHT Score: ", std_dev_score)
        printf("Max PNR-FLIGHT Score: ", df["allocated_flights_score"].max())
        printf("Min PNR-FLIGHT Score: ", df["allocated_flights_score"].min())
        printf(DIVIDER)

        tap = 0
        for _, row in df.iterrows():
            if type(row["allocated_src"]) == str:
                tap += int(row["pax"])

        printf("Allocation Stats")
        total = df["pnr"].count()
        allocated = df["allocated_src"].count()
        printf("Total pnr: ", total)
        printf("Total allocated pnr: ", allocated)
        printf("Total unallocated pnr: ", total - allocated)
        printf("Total Passengers: ", df["pax"].sum())
        printf("Total Allocatted passengers: ", tap)

        printf(DIVIDER)
        printf("Connection Stats")

        conn = [0, 0, 0, 0]
        for x in df["allocated_flights"]:
            # laod to a list
            x = ast.literal_eval(x)
            conn[len(x)] += 1

        printf("Unallocated : ", conn[0])
        printf("Direct : ", conn[1])
        printf("One Stop : ", conn[2])
        printf("Two Stop : ", conn[3])

        printf(DIVIDER)
        class_map = {"F": 0, "B": 1, "P": 2, "E": 3}
        flight_stats = {}
        for _, row in df.iterrows():
            r_flight = ast.literal_eval(row["canclled_flight"])[0]
            if r_flight not in flight_stats:
                flight_stats[r_flight] = {
                    "total_pnr": 0,
                    "allocated_pnr": 0,
                    "unallocated_pnr": 0,
                    "allocated_passengers": 0,
                    "unallocated_passengers": 0,
                    "upgraded_pnr": 0,
                    "samestate_pnr": 0,
                    "downgraded_pnr": 0,
                    "allocated_flight": {},
                    "default_flight": None,
                    "default_allocation": 0
                }

            flight_stats[r_flight]["total_pnr"] += 1
            if type(row["allocated_src"]) == str:
                flight_stats[r_flight]["allocated_pnr"] += 1
                flight_stats[r_flight]["allocated_passengers"] += int(row["pax"])
            else:
                flight_stats[r_flight]["unallocated_pnr"] += 1
                flight_stats[r_flight]["unallocated_passengers"] += int(row["pax"])


            if type(row["allocated_src"]) == str:
                r_class_score = float(class_map[row["canclled_class"]])
                a_class_score = sum([class_map[x] for x in ast.literal_eval(row["allocated_classes"])]) / max(
                    len(ast.literal_eval(row["allocated_classes"])), 1
                )
                # printf(r_class_score, a_class_score, row["canclled_class"], ast.literal_eval(row["allocated_classes"]))
                if r_class_score > a_class_score:
                    flight_stats[r_flight]["upgraded_pnr"] += 1
                elif r_class_score < a_class_score:
                    flight_stats[r_flight]["downgraded_pnr"] += 1
                else:
                    flight_stats[r_flight]["samestate_pnr"] += 1

                k = tuple(ast.literal_eval(row["allocated_flights"]))
                if flight_stats[r_flight]["allocated_flight"].get(k) is None:
                    flight_stats[r_flight]["allocated_flight"][k] = 0
                flight_stats[r_flight]["allocated_flight"][k] += 1

        for flight, details in flight_stats.items():
            max_count = 0
            max_flight = None
            for k, v in details["allocated_flight"].items():
                if v > max_count:
                    max_count = v
                    max_flight = k
            flight_stats[flight]["default_flight"] = max_flight
            flight_stats[flight]["default_allocation"] = max_count


        printf(f"Cancelled Flight Level Stats saved in : {self.filename.split('.')[0]}.flight_stats.csv")
        printf("Total Cancelled Flights: ", len(flight_stats))
        flight_stats_df = pd.DataFrame(flight_stats).T
        flight_stats_df.to_csv(f"{self.filename.split('.')[0]}.flight_stats.csv")

        df['canclled_flight_arrival'] = pd.to_datetime(df['canclled_flight_arrival'])
        df['allocated_flights_arrival'] = pd.to_datetime(df['allocated_flights_arrival'])

        # Calculate the delay
        df['delay'] = (df['allocated_flights_arrival'] - df['canclled_flight_arrival']).dt.total_seconds() / 3600
        printf(DIVIDER)
        printf("Delay Stats")
        printf("Mean Delay: ", df['delay'].mean())
        printf("Std Dev. Delay: ", df['delay'].std())
        printf("Max Delay: ", df['delay'].max())

        f.close()


    def process_result(self):
        # current columns ->
        #   pnr : [ inv_id, class, score ]
        #   processesed_column :
        #   pnr, pnr_score, canclled_flight, canclled_cabin, canclled_flight_departure, canclled_flight_arrival, \
        #       allocated_flights, allocated_flights_departure, allocated_flights_arrival, allocated_class,mallocated_flights_score

        cancelled_flights = Flight.objects.filter(status="Cancelled")
        pnr_flights = PnrFlightMapping.objects.filter(flight__in=cancelled_flights)

        pnr_flight_map = {}
        for pnr_flight in pnr_flights:
            pnr_flight_map[pnr_flight.pnr.pnr] = [pnr_flight.pnr, pnr_flight.flight]

        self.data = []
        for pnr, allocation in self.result.items():
            # print(allocation, type(allocation))
            pnr_obj, cancelled_flight = pnr_flight_map[pnr]

            if allocation is None or allocation == "NULL" or allocation == ["NULL"]:
                allocated_flights = []
            elif type(allocation[0]) is not list:
                allocated_flights = [allocation[0]]
            else:
                allocated_flights = allocation[0]

            if allocation is None or allocation == "NULL" or allocation == ["NULL"]:
                allocated_class = []
            elif type(allocation[1]) is not list:
                allocated_class = [allocation[1]]
            else:
                allocated_class = allocation[1]

            # allocated_class = [CABIN_CLASS_MAPPING[c] for c in allocated_class]

            score = (
                allocation[2]
                if allocation is not None
                and allocation != ["NULL"]
                and type(allocation[2]) == float
                else -1.0
            )

            if allocated_flights and len(allocated_flights) > 0:
                alt_filght = Flight.objects.get(flight_id=allocated_flights[0])
                alt_filght_departure = alt_filght.departure
                alt_flight_src = alt_filght.src

                alt_filght = Flight.objects.get(flight_id=allocated_flights[-1])

                alt_filght_arrival = alt_filght.arrival
                alt_flight_dst = alt_filght.dst
                flight_time = datetime.timedelta(0)
                for flight_id in allocated_flights:
                    flight = Flight.objects.get(flight_id=flight_id)
                    flight_time += flight.arrival - flight.departure
                flight_time = flight_time / len(allocated_flights)
            else:
                alt_filght_departure = None
                alt_filght_arrival = None
                alt_flight_src = None
                alt_flight_dst = None
                flight_time = None

            self.data.append(
                [
                    pnr,
                    pnr_obj.pax,
                    pnr_obj.score,
                    [cancelled_flight.flight_id],
                    CABIN_CLASS_MAPPING[pnr_obj.seat_class.type_name],
                    cancelled_flight.departure,
                    cancelled_flight.arrival,
                    cancelled_flight.src,
                    cancelled_flight.dst,
                    alt_flight_src,
                    alt_flight_dst,
                    allocated_flights,
                    alt_filght_departure,
                    alt_filght_arrival,
                    allocated_class,
                    flight_time,
                    score,
                ]
            )
        # pass

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.config = load_settings(options["config"])
        fn_flight_ranking = self.wrapper_flight_ranking(self)

        alpha=self.config["search"].get("alpha",4)
        beta=self.config["search"].get("beta", 0.3)

        timer = time.time()
        if self.config["search"]["skip_quantum"]:
            self.allocator = PnrReallocation(
                get_alt_flights_fn=fn_flight_ranking,
                get_pnr_fn=util_pnr_ranking,
                get_cancled_fn=cancelled_flight,
                upgrade=self.config["search"]["upgrade"],
                downgrade=self.config["search"]["downgrade"],
                alpha=alpha, beta=beta
            )
        else:
            self.allocator = QuantumReallocation(
                get_alt_flights_fn=fn_flight_ranking,
                get_pnr_fn=util_pnr_ranking,
                get_cancled_fn=cancelled_flight,
                upgrade=self.config["search"]["upgrade"],
                downgrade=self.config["search"]["downgrade"],
                alpha=alpha, beta=beta
            )
        print("Time taken for data-loading : ", time.time() - timer, " seconds")

        timer = time.time()
        self.result = self.allocator.allocate()
        print("Time taken for allocation : ", time.time() - timer, " seconds")
        # print(self.result)
        self.process_result()
        self.savefile(options["save"])
        self.generate_report()
