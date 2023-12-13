import datetime
import pandas as pd
from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import *
from flight.management.commands.populate_basic import Command as PopulateBasicCommand
from flight.management.commands.populate_airport import Command as PopulateAirportCommand
from flight.management.commands.populate_aircraft import Command as PopulateAircraftCommand

SCHEDULE_FILE="flight/management/data/schedule_table.csv"
FLIGHT_FILE="flight/management/data/flight_inventory_table.csv"
PNR_FILE="flight/management/data/pnr_table.csv"
PASSENGER_FILE="flight/management/data/passenger_table.csv"


class Command(BaseCommand):
    help = "Randomly cancels x% of the flights"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clean",
            type=bool,
            default=False,
            help="Clean all cancelled flights",
        )

    def load_dataframes(self):
        self.schedule_df = pd.read_csv(SCHEDULE_FILE)
        self.flight_df = pd.read_csv(FLIGHT_FILE)
        self.pnr_df = pd.read_csv(PNR_FILE)
        self.passenger_df = pd.read_csv(PASSENGER_FILE)

    def check_missing_iata(self):
        # ingest
        PopulateAirportCommand.clean()
        PopulateAirportCommand.populate_airport()

        missing_iata = set()
        # check if all iata exists
        for iata in self.schedule_df["DepartureAirport"].unique():
            if Airport.objects.filter(iata_code=iata.strip()).exists():
                continue
            else:
                missing_iata.add(iata)
        
        for iata in self.schedule_df["ArrivalAirport"].unique():
            if Airport.objects.filter(iata_code=iata.strip()).exists():
                continue
            else:
                missing_iata.add(iata)

        if len(missing_iata) > 0:
            print("Missing iata codes:")
            print(missing_iata)
            print("Please add the missing iata codes to the Airport table")
        else:
            print("All iata codes exists in the Airport table")

    def load_basic(self):
        PopulateBasicCommand.clean()
        PopulateBasicCommand.populate_basics()

    def load_aircraft(self):
        PopulateAircraftCommand.clean()
        PopulateAircraftCommand.populate()

    def handle(self, *args: Any, **options: Any) -> str | None:
        if options["clean"]:
            print("Cleaned all cancelled flights")
            return
        
        # no need to populate the Airport table
        # only check if all iata exists
        self.load_dataframes()
        self.check_missing_iata()

        # check basic data
        print("Checking basic data")
        self.load_basic()

        # start main process
        # schedule ( aircraft, seat_distribution , SehcduleDate, Schdule) 
        # Flights/Inventory -> PNR | Passenger

        self.load_aircraft()
        # self.laod_flight_schedule()
        # self.load_flight_inventory()
        # self.load_pnr()
        
