import csv
import time
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

# print(CABIN_CLASS_MAPPING)


class Command(BaseCommand):
    help = "Allocates alternate flights for cancelled flights"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--config",
            type=str,
            default="settings.yml",
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
        with open(filename, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "pnr",
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
                    "allocated_flights_score",
                ]
            )
            for row in self.data:
                writer.writerow(row)

        print("Result saved result in file : ", filename)

    def generate_report(self):
        pass

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
            pnr_obj, cancelled_flight = pnr_flight_map[pnr]

            if allocation is None or allocation == "NULL":
                allocated_flights = []
            elif type(allocation[0]) is not list:
                allocated_flights = [allocation[0]]
            else:
                allocated_flights = allocation[0]

            if allocation is None or allocation == "NULL":
                allocated_class = []
            elif type(allocation[1]) is not list:
                allocated_class = [allocation[1]]
            else:
                allocated_class = allocation[1]

            # allocated_class = [CABIN_CLASS_MAPPING[c] for c in allocated_class]

            score = allocation[2] if allocation is not None else 1e15

            if allocated_flights and len(allocated_flights) > 0:
                alt_filght = Flight.objects.get(flight_id=allocated_flights[0])
                alt_filght_departure = alt_filght.departure
                alt_flight_src = alt_filght.src

                alt_filght = Flight.objects.get(flight_id=allocated_flights[-1])

                alt_filght_arrival = alt_filght.arrival
                alt_flight_dst = alt_filght.dst
            else:
                alt_filght_departure = None
                alt_filght_arrival = None
                alt_flight_src = None
                alt_flight_dst = None

            self.data.append(
                [
                    pnr,
                    pnr_obj.score,
                    [cancelled_flight.flight_id],
                    pnr_obj.seat_class,
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
                    allocation[2],
                ]
            )
        # pass

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.config = load_settings(options["config"])
        fn_flight_ranking = self.wrapper_flight_ranking(self)

        timer = time.time()
        if self.config["search"]["skip_quantum"]:
            self.allocator = PnrReallocation(
                get_alt_flights_fn=fn_flight_ranking,
                get_pnr_fn=util_pnr_ranking,
                get_cancled_fn=cancelled_flight,
                upgrade=False,
                downgrade=False,
            )

        else:
            self.allocator = QuantumReallocation(
                get_alt_flights_fn=fn_flight_ranking,
                get_pnr_fn=util_pnr_ranking,
                get_cancled_fn=cancelled_flight,
            )
        print("Time taken for data-loading : ", time.time() - timer, " seconds")

        timer = time.time()
        self.result = self.allocator.allocate()
        print("Time taken for allocation : ", time.time() - timer, " seconds")
        # print(self.result)
        self.process_result()
        self.savefile()
