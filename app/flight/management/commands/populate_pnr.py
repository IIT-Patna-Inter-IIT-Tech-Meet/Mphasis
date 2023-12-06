from io import StringIO
import uuid
import random
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import PNR, PnrFlightMapping, PnrPassenger, Flight, SeatDistribution
from faker import Faker
from app.config import settings

fake = Faker()


class Command(BaseCommand):
    help = "populate passengers and the tables : PNR, PNRFlightMapping, PnrPassenger\n--clean: clear the passengers and pnr tables"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pnrs = []
        self.pnr_passengers = []
        self.pnr_flight_mappings = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

    def clean(self):
        with transaction.atomic():
            PnrFlightMapping.objects.all().delete()
            PnrPassenger.objects.all().delete()
            PNR.objects.all().delete()
        print("Cleaned")

    def populate_PNR(self):
        seat_distributions = SeatDistribution.objects.all()
        # bulk fetch
        all_pnr = set()
        sd = {}
        for seat in seat_distributions:
            if seat.aircraft_id not in sd:
                sd[seat.aircraft_id] = []
            sd[seat.aircraft_id].append(seat)
        
        flights = Flight.objects.all().order_by("departure")
        for flight in flights:
            seats = sd[flight.schedule.schedule.aircraft_id]
            total_seats = flight.schedule.schedule.aircraft.total_capacity
            tofill = (total_seats * random.randint(60, 80)) // 100
            for seat in seats:
                if tofill <= 0:
                    break
                
                if seat.seat_count <= 0:
                    continue
                
                c = seat.seat_count - random.randint(0, seat.seat_count*2//5)
                while c > 0:
                    tofill = random.randint(1, min(5, c))
                    c-= tofill

                    # maintain unique 
                    id = str(uuid.uuid4())[:6]
                    while id in all_pnr:
                        id = str(uuid.uuid4())[:6]
                    all_pnr.add(id)

                    pnr = PNR.objects.create(
                        pnr_id=id,
                        seat_class=seat.class_type,
                        booking_type=random.choice(["Individual", "Group"]),
                        booking_date=datetime.now(),
                        fare=flight.fare,
                        tax=flight.tax,
                        total_fare=flight.total_fare,
                    )
                



    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            return

        self.populate_PNR()
