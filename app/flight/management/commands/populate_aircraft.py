from django.db import transaction
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Aircraft, SeatDistribution, ClassType
import pandas as pd
from app.config import settings

SAFE = settings["data_generation"]["safe"]

class Command(BaseCommand):
    help = "polulate Aircraftt, SeatDistribution"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

    @staticmethod
    def clean():
        with transaction.atomic():
            SeatDistribution.objects.all().delete()
            Aircraft.objects.all().delete()
        print("Cleaned")

    @staticmethod
    def populate():
        df_aircraft = pd.read_csv("flight/management/data/aircrafts.csv")
        df_sd = pd.read_csv("flight/management/data/seat-distribution.csv")

        classes = ClassType.objects.all()
        classes = {c.type_name: c for c in classes}

        aircrafts = {}
        seat_distributions = []

        for i in range(len(df_aircraft)):
            # safe insertion
            unique = True
            if SAFE:
                try:
                    Aircraft.objects.get(registration=df_aircraft["registration"][i])
                    unique = False
                except Aircraft.DoesNotExist:
                    pass
            if unique:
                aircraft = Aircraft(
                    id = df_aircraft["id"][i],
                    model=df_aircraft["model"][i],
                    name=df_aircraft["name"][i],
                    registration=df_aircraft["registration"][i],
                    owner_code=df_aircraft["owner_code"][i],
                    owner_name=df_aircraft["owner_name"][i],
                    total_capacity=df_aircraft["total_capacity"][i],
                    total_invenotry=df_aircraft["total_inventory"][i],
                )
                aircrafts[df_aircraft["id"][i]] = aircraft

        if len(aircrafts) > 0:
            Aircraft.objects.bulk_create(aircrafts.values())
        print(f"Added {len(aircrafts)} aircraft instances.")

        # add seat distribution
        for i in range(len(df_sd)):
            aircraft = aircrafts[df_sd["aircraft_id"][i]]
            class_type = classes[df_sd["class"][i]]
            seat_distribution = SeatDistribution(
                aircraft_id=aircraft,
                class_type=class_type,
                seat_count=df_sd["seat_count"][i],
            )
            seat_distributions.append(seat_distribution)


        if len(seat_distributions) > 0:
            SeatDistribution.objects.bulk_create(seat_distributions)
        print(f"Added {len(seat_distributions)} seat distribution instances.")

    def handle(self, *args, **options):
        """
        Tables:
        - Aircraft
            - id, registration, ownercode -> random string
            - total capcity -> random int
        - SeatDistribution
        """
        if options["clean"]:
            self.clean()

        self.populate()

        