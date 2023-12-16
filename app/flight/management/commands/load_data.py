import ast
import pytz
import datetime
import pandas as pd
from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from datetime import timezone
from flight.models import *
from flight.management.commands.populate_basic import Command as PopulateBasicCommand
from flight.management.commands.populate_airport import (
    Command as PopulateAirportCommand,
)
from flight.management.commands.populate_aircraft import (
    Command as PopulateAircraftCommand,
)
from app.config import settings

TIMEZONE = pytz.timezone("Asia/Kolkata")

SCHEDULE_FILE = settings["data_generation"]["schedule_file"]
FLIGHT_FILE = settings["data_generation"]["flight_file"]
PNR_FILE = settings["data_generation"]["pnr_file"]
PASSENGER_FILE = settings["data_generation"]["pax_file"]


COLUMN_MAP = {
    "id": "ScheduleID",
    "carrier_cd": "CarrierCode",
    "aircraft_id": "AircraftTailNumber",
    "departure_airport": "DepartureAirport",
    "arrival_airport": "ArrivalAirport",
    "departure_time": "DepartureTime",
    "arrival_time": "ArrivalTime",
    "start_date": "StartDate",
    "end_date": "EndDate",
    "r_sun": "Sunday",
    "r_mon": "Monday",
    "r_tue": "Tuesday",
    "r_wed": "Wednesday",
    "r_thu": "Thursday",
    "r_fri": "Friday",
    "r_sat": "Saturday",
    "freq": "Frequency_per_week",
    "dept_count": "NoOfDepartures",
    "status": "Status",
}

FLIGHT_CMAP = {
    "flight_id": "InventoryId",
    "schedule": "ScheduleId",
    "status": "?",
    "departure": "DepartureDateTime",
    "arrival": "ArrivalDateTime",
    "src": "DepartureAirport",
    "dst": "ArrivalAirport",
    "avilable_inventory": [
        "FC_AvailableInventory",
        "BC_AvailableInventory",
        "PC_AvailableInventory",
        "EC_AvailableInventory",
    ],
    "dep_key": "Dep_Key",
}

PNR_CMAP = {
    "pnr": "RECLOC",
    "dep_key": "DEP_KEY",
    "status": "ACTION_CD",
    "seat_class": "COS_CD",
    "seg_seq": "SEG_SEQ",
    "carrier_cd": "CARRIER_CD",
    "paid_service": 0,
    "loyalty_program": 0,
    "conn": "SEG_TOTAL",
    "pax": "PAX_CNT",
    "booking_type": "NA",
}

PASSENGER_CMAP = {
    "recloc": "RECLOC",
    "last_name": "LAST_NAME",
    "first_name": "FIRST_NAME",
    "nationality": "NATIONALITY",
    "contact_no": "CONTACT_PH_NUM",
    "contact_email": "CONTACT_EMAIL",
    "doc_id": "DOC_ID",
    "doc_type": "DOC_TYPE",
    "scd1": "SPECIAL_NAME_CD1",
    "scd2": "SPECIAL_NAME_CD2",
    "ssr": "SSR_CODE_CD1",
    "loyalty": "TierLevel",
}


class Command(BaseCommand):
    help = "Randomly cancels x% of the flights"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.schedule_df = pd.read_csv(SCHEDULE_FILE)  # df_sch
        self.flight_df = pd.read_csv(FLIGHT_FILE)  # df_inv
        self.pnr_df = pd.read_csv(PNR_FILE)  # df_pnrb
        self.passenger_df = pd.read_csv(PASSENGER_FILE)  # df_pnrp

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

    def load_airports(self):
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

        # get a local lookup table
        airports = Airport.objects.all()
        self.airport_map = {}
        for airport in airports:
            self.airport_map[airport.iata_code] = airport

    def load_basic(self):
        PopulateBasicCommand.clean()
        PopulateBasicCommand.populate_basics()

        carriers = Carrier.objects.all()
        self.carrier_map = {}
        for carrier in carriers:
            self.carrier_map[carrier.code] = carrier

        # fetch all ssr
        ssrs = SSR.objects.all()
        self.ssr_map = {}
        for ssr in ssrs:
            self.ssr_map[ssr.ssr_name] = ssr

        # fetch all class
        classes = ClassType.objects.all()
        self.class_map = {}
        for class_type in classes:
            self.class_map[class_type.type_name] = class_type

    def load_aircraft(self):
        PopulateAircraftCommand.clean()
        PopulateAircraftCommand.populate()

        # load aircraft_map
        self.aircraft_map = {}
        aircrafts = Aircraft.objects.all()
        for aircraft in aircrafts:
            self.aircraft_map[aircraft.registration] = aircraft

    def load_flight_schedule(self):
        # clean first
        FlightSchedule.objects.all().delete()

        # load schedule
        self.shcedules_map = {}
        self.shcedule_date_map = {}

        for index, row in self.schedule_df.iterrows():
            start_date = datetime.datetime.strptime(
                row[COLUMN_MAP["start_date"]], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            end_date = datetime.datetime.strptime(
                row[COLUMN_MAP["end_date"]], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")

            schedule = FlightSchedule(
                id=row[COLUMN_MAP["id"]],
                carrier_cd=self.carrier_map[row[COLUMN_MAP["carrier_cd"]]],  # fj
                aircraft_id=self.aircraft_map[row[COLUMN_MAP["aircraft_id"]]],  # fk
                departure_airport=self.airport_map[
                    row[COLUMN_MAP["departure_airport"]].strip()
                ],  # fk
                arrival_airport=self.airport_map[
                    row[COLUMN_MAP["arrival_airport"]].strip()
                ],  # fk
                departure_time=row[COLUMN_MAP["departure_time"]],  # fk
                arrival_time=row[COLUMN_MAP["arrival_time"]],  # fk
                start_date=start_date,  # fk
                end_date=end_date,  # fk
                r_sun=bool(row[COLUMN_MAP["r_sun"]]),  # fk
                r_mon=bool(row[COLUMN_MAP["r_mon"]]),  # fk
                r_tue=bool(row[COLUMN_MAP["r_tue"]]),  # fk
                r_wed=bool(row[COLUMN_MAP["r_wed"]]),  # fk
                r_thr=bool(row[COLUMN_MAP["r_thu"]]),  # b
                r_fri=bool(row[COLUMN_MAP["r_fri"]]),  # b
                r_sat=bool(row[COLUMN_MAP["r_sat"]]),  # b
                freq=int(row[COLUMN_MAP["freq"]]),  # int
                dept_count=int(row[COLUMN_MAP["dept_count"]]),  # int
                status=row[COLUMN_MAP["status"]],
            )

            self.shcedules_map[schedule.id] = schedule

            # create schedule dates
            departure_dates = row["DepartureDates"]
            departure_dates = ast.literal_eval(departure_dates)
            departure_dates = [
                datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
                for date in departure_dates
            ]

            for date in departure_dates:
                schedule_date = FlightScheduleDate(schedule=schedule, date=date)
                self.shcedule_date_map[(schedule.id, date)] = schedule_date

        with transaction.atomic():
            FlightSchedule.objects.bulk_create(self.shcedules_map.values())
            print(f"Loaded {len(self.shcedules_map)} flight schedules")

            FlightScheduleDate.objects.bulk_create(self.shcedule_date_map.values())
            print(f"Loaded {len(self.shcedule_date_map)} flight schedule dates")

    def load_flight_inventory(self):
        # clean first
        Flight.objects.all().delete()

        # print(self.airport_map)

        self.inventory_map = {}
        for _, row in self.flight_df.iterrows():
            schedule = self.shcedules_map[row["ScheduleId"]]
            date = datetime.datetime.strptime(
                row["DepartureDate"], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
            schedule_date = self.shcedule_date_map[(row["ScheduleId"], date)]
            departure = datetime.datetime.strptime(
                row[FLIGHT_CMAP["departure"]], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=TIMEZONE)

            arrival = datetime.datetime.strptime(
                row[FLIGHT_CMAP["arrival"]], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=TIMEZONE)

            avilable_inventory = []
            for col in FLIGHT_CMAP["avilable_inventory"]:
                avilable_inventory.append(row[col])
            # inv_map = ",".join(list(map(str, avilable_inventory)))

            inventory = Flight(
                flight_id=row[FLIGHT_CMAP["flight_id"]],
                schedule=schedule_date,
                status=schedule_date.schedule.status,
                departure=departure,
                arrival=arrival,
                src=self.airport_map[row[FLIGHT_CMAP["src"]].strip()],
                dst=self.airport_map[row[FLIGHT_CMAP["dst"]].strip()],
                avilable_inventory=",".join(list(map(str, avilable_inventory))),
                dep_key=row[FLIGHT_CMAP["dep_key"]][:-2],
            )
            self.inventory_map[inventory.dep_key] = inventory

        with transaction.atomic():
            Flight.objects.bulk_create(self.inventory_map.values())
            print(f"Loaded {len(self.inventory_map)} flight inventory")

    def load_pnr(self):
        # clean first
        PnrPassenger.objects.all().delete()
        PnrFlightMapping.objects.all().delete()
        PNR.objects.all().delete()

        # fetch all passengers
        passengers = {}
        for _, row in self.passenger_df.iterrows():
            pnr = row[PASSENGER_CMAP["recloc"]]
            if pnr not in passengers:
                passengers[pnr] = []
            passengers[pnr].append(row)

        # load pnr
        self.pnr_map = {}
        self.pnr_flight_map = {}
        self.passenger_list = []

        seat_class_map = {
            "FirstClass": "F",
            "BusinessClass": "C",
            "PremiumEconomyClass": "R",
            "EconomyClass": "E",
        }

        score = 0

        for _, row in self.pnr_df.iterrows():
            pnr = PNR(
                pnr=row[PNR_CMAP["pnr"]],
                dep_key=row[PNR_CMAP["dep_key"]],
                status="ok",
                seat_class=self.class_map[seat_class_map[row[PNR_CMAP["seat_class"]]]],
                seg_seq=row[PNR_CMAP["seg_seq"]],
                carrier_cd=self.carrier_map[row[PNR_CMAP["carrier_cd"]]],
                paid_service=PNR_CMAP["paid_service"],
                loyalty_program=PNR_CMAP["loyalty_program"],
                conn=int(row[PNR_CMAP["conn"]]),
                pax=int(row[PNR_CMAP["pax"]]),
                # booking_type=PNR_CMAP["booking_type"],
                score=score,
            )
            pnr.score = pnr.seat_class.score
            pnr_flight = PnrFlightMapping(
                pnr=pnr,
                flight=self.inventory_map[row[PNR_CMAP["dep_key"]]],
            )

            # load passengers
            for passenger in passengers[pnr.pnr]:
                score, ssr = 0, 0
                if passenger[PASSENGER_CMAP["ssr"]] in self.ssr_map:
                    # print(passenger[PASSENGER_CMAP["ssr"]], type(passenger[PASSENGER_CMAP["ssr"]]))
                    score += self.ssr_map[passenger[PASSENGER_CMAP["ssr"]]].ssr_point
                    ssr = 1

                if passenger[PASSENGER_CMAP["scd1"]] != "":
                    score += settings["scores"]["default_scd1_score"]

                if passenger[PASSENGER_CMAP["scd2"]] != "":
                    score += settings["scores"]["default_scd2_score"]

                if (
                    passenger[PASSENGER_CMAP["loyalty"]]
                    in settings["scores"]["loyalty"]
                ):
                    score += settings["scores"]["loyalty"][
                        passenger[PASSENGER_CMAP["loyalty"]]
                    ]

                pnr.score += score
                passenger = PnrPassenger(
                    recloc=pnr,
                    last_name=passenger[PASSENGER_CMAP["last_name"]],
                    first_name=passenger[PASSENGER_CMAP["first_name"]],
                    nationality=passenger[PASSENGER_CMAP["nationality"]],
                    contact_no=passenger[PASSENGER_CMAP["contact_no"]],
                    contact_email=passenger[PASSENGER_CMAP["contact_email"]],
                    doc_id=passenger[PASSENGER_CMAP["doc_id"]],
                    doc_type=passenger[PASSENGER_CMAP["doc_type"]],
                    scd1=passenger[PASSENGER_CMAP["scd1"]],
                    scd2=passenger[PASSENGER_CMAP["scd2"]],
                    ssr=ssr,
                )

                self.passenger_list.append(passenger)

            self.pnr_map[pnr.pnr] = pnr
            self.pnr_flight_map[pnr.pnr] = pnr_flight

        with transaction.atomic():
            PNR.objects.bulk_create(self.pnr_map.values())
            print(f"Loaded {len(self.pnr_map)} pnr")

            PnrFlightMapping.objects.bulk_create(self.pnr_flight_map.values())
            print(f"Loaded {len(self.pnr_flight_map)} pnr flight mapping")

            PnrPassenger.objects.bulk_create(self.passenger_list)
            print(f"Loaded {len(self.passenger_list)} pnr passengers")

    def handle(self, *args: Any, **options: Any) -> str | None:
        if options["clean"]:
            print("Cleaned all cancelled flights")
            return

        # no need to populate the Airport table
        # only check if all iata exists
        self.load_dataframes()
        self.load_airports()

        # check basic data
        print("Checking basic data")
        self.load_basic()

        # start main process
        # schedule ( aircraft, seat_distribution , SehcduleDate, Schdule)
        # Flights/Inventory -> PNR | Passenger

        self.load_aircraft()
        self.load_flight_schedule()
        self.load_flight_inventory()

        # laod pnr ``
        self.load_pnr()
