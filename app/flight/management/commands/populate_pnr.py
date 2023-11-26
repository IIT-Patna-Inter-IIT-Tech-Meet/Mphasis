import uuid
import random
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import Passenger, Flight, PNR, SeatDistribution
from faker import Faker
from app.config import settings

fake = Faker()


class Command(BaseCommand):
    help = "populate passengers and the pnr tables\n--clean: clear the passengers and pnr tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

    def clean(self):
        with transaction.atomic():
            PNR.objects.all().delete()
            Passenger.objects.all().delete()
        print("Cleaned")

    def populate_PNR(self):
        # Get all flight in sorted order of departure date
        flights = Flight.objects.all().order_by("departure_time")
        # for each flight, check the total seats, decide how many seats to book (constant probability)
        for flight in flights:
            seats = SeatDistribution.objects.get(aircraft_id=flight.aircraft_id)
            for seat in seats:
                tofill_seats = (seat.seat_count * random.randint(60, 80)) // 100
                while tofill_seats > 0:
                    self.create_pnr(flight, seat.class_type)
                    # create a new pnr
        # for each seat, until the seat is full, book a pnr ( seat = seat -n  ) where n = random.randint(1, 9)

        # add some connecting flight :
        # A -> B , B -> C , C -> D |   A -> B, B -> A
        # A -> B  | dst = A,

    def create_pnr(self, flight, class_type):
        pnr = str(uuid.uuid4())[:6]
        passenger = self.create_passenger()
        paid_service = random.randint(0, 100) < settings.get("paid_service_probability")*100
        loyality_program = random.randint(0, 100) < settings.get("loyality_program_probability")*100

        pax_probs = settings.get("pax_probability")
        outcomes = pax_probs.keys()
        pax = random.choices(outcomes, weights=pax_probs.values())[0]

        pnr = PNR.objects.create(
            pnr=pnr,
            passenger=passenger,
            flight=flight,
            seat_class=class_type,
            currency="INR",
            paid_service=paid_service,
            loyalty_program=loyality_program,
            conn=0,
            pax=pax,
            
        )

    def create_passenger(self):
        name = fake.name()
        passenger = Passenger.objects.create(
            name=name,
            email=f"{name}@example.com",
            phone=random.randint(1000000000, 9999999999),
        )
        passenger.save()
        return passenger

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            return

        self.populate_PNR()
