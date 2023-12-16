from django.core.management.base import BaseCommand
from flight.models import Airport
from tqdm import trange, tqdm


class Command(BaseCommand):
    help = """
    Usages : python3 manage.py populate <table_name> <filename>
    """

    all_tables = {"airport": Airport}

    @staticmethod
    def clean():
        Airport.objects.all().delete()

    def handle(self, *args, **options):
        if options["clean"]:
            delete_all(self.all_tables[options["tablename"]])

        self.populate_airport()

    def add_arguments(self, parser):
        parser.add_argument(
            "--tablename",
            type=str,
            help="Table name to populate",
            default="airport",
            nargs="?",
        )
        parser.add_argument(
            "--filename",
            type=str,
            help="Filename to populate from",
            default="flight/management/data/in-airports.csv",
            nargs="?",
        )
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Delete all data from table before populating",
        )

    @staticmethod
    def populate_airport(filename="flight/management/data/in-airports.csv"):
        import csv

        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            airports = []
            for row in reader:
                if row["iata_code"] == "":
                    continue
                airport = Airport()
                airport.id = row["id"]
                airport.ident = row["ident"]
                airport.type = row["type"]
                airport.name = row["name"]
                airport.latitude_deg = row["latitude_deg"]
                airport.longitude_deg = row["longitude_deg"]
                airport.elevation_ft = (
                    int(row["elevation_ft"]) if row["elevation_ft"] else None
                )
                airport.continent = row["continent"]
                airport.continent_name = row["continent"]
                airport.iso_country = row["iso_country"]
                airport.iso_region = row["iso_region"]
                airport.local_region = row["local_region"]
                airport.municipality = row["municipality"]
                airport.scheduled_service = row["scheduled_service"]
                airport.gps_code = row["gps_code"]
                airport.iata_code = row["iata_code"]
                airport.local_code = row["local_code"]
                airport.home_link = row["home_link"]
                airport.wikipedia_link = row["wikipedia_link"]
                airport.keywords = row["keywords"]
                airport.score = row["score"]
                airports.append(airport)
                # airport.save()
            Airport.objects.bulk_create(airports)
            print(f"Added {len(airports)} to the database")


def delete_all(tb_model):
    tb_model.objects.all().delete()
    print(f"Deleted all data from {tb_model.__name__}")
