from io import StringIO
import uuid
import random
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import Passenger, Flight,SSR, PNR, SeatDistribution, Group, PnrFlightMapping
from faker import Faker
from app.config import settings

fake = Faker()


class Command(BaseCommand):
    help = "populate passengers and the pnr tables\n--clean: clear the passengers and pnr tables"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking_options = list(Group.objects.all())
        self.booking_options_weights = [booking_type.probability for booking_type in self.booking_options]
        self.all_ssr = SSR.objects.all()

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
            PnrFlightMapping.objects.all().delete()
        print("Cleaned")

    def populate_PNR(self):
        # Get all flight in sorted order of departure date
        flights = Flight.objects.all().order_by("departure_time")
        # for each flight, check the total seats, decide how many seats to book (constant probability)
        for flight in flights:
            # bulk_pnrmap = []
            seats = SeatDistribution.objects.filter(aircraft_id=flight.aircraft_id)
            for seat in seats:
                tofill_seats = (seat.seat_count * random.randint(60, 80)) // 100
                while tofill_seats > 0:
                    cfp : float = float(settings.get("connecting").get("probability", 0))
                    connecting_flight = random.choices([True, False], weights=[cfp, 1- cfp])[0]
                    # create a new pnr
                    if not connecting_flight:
                        c, pnr = self.create_pnr( seat.class_type)
                        tofill_seats -= c

                        # add pnr-flight
                        with transaction.atomic():
                            p = PnrFlightMapping.objects.create(pnr=pnr, flight=flight)
                            p.save()
                    else:
                        # check for a pnr with dst = flight.src, also cabin_class = seat.class_type
                        candidates = PnrFlightMapping.objects.filter(flight__arrival_airport_id=flight.departure_airport_id, flight__arrival_time__lt=flight.departure_time, pnr__seat_class=seat.class_type)
                        if len(candidates) > 0:
                            print(f"Found {len(candidates)} for connecting flight")
                            rand_pnr = random.choice(candidates)
                            pnr = rand_pnr.pnr
                            pnr.conn += 1
                            pnr.score += int(settings.get("connecting").get("score", 0))
                            pnr.save()
                            with transaction.atomic():
                                p = PnrFlightMapping.objects.create(pnr=pnr, flight=flight)
                                p.save()
                            tofill_seats -= int(pnr.pax)
            print(f"Finished populating flight {flight}")


    def create_pnr(self, class_type):
        pnr = str(uuid.uuid4())[:6]
        # check if the pnr already exists
        while PNR.objects.filter(pnr=pnr).exists():
            pnr = str(uuid.uuid4())[:6]
        passenger = self.create_passenger()
        paid_service = random.randint(0, 100) < settings.get("paid_service")*100
        loyality_program = random.randint(0, 100) < settings.get("loyality")*100

        pax_probs = settings.get("pax_probability")
        outcomes = list(pax_probs.keys())
        pax = random.choices(outcomes, weights=pax_probs.values())[0]
        booking = random.choices(self.booking_options, weights=self.booking_options_weights)[0]
        ssr, ssr_score = self.getssr()

        score = 0
        if paid_service: score += int(settings.get("paid_service_score"))
        if loyality_program: score += int(settings.get("loyality_program_score"))
        score += ssr_score
        score += int(settings.get("pax_score"))*pax
        score += int(booking.group_point)
        score += int(class_type.score)
        with transaction.atomic():
            pnr = PNR.objects.create(
                pnr=pnr,
                passenger=passenger,
                seat_class=class_type,
                currency="INR",
                paid_service=paid_service,
                loyalty_program=loyality_program,
                conn=0,
                pax=pax,
                booking_type=booking,
                ssr=ssr,
                score = score,
            )
            pnr.save()
        print(f"Created PNR {pnr}: {score}")
        return pax, pnr

    def getssr(self):
        ssr_val,count = 0, 0
        for ssr in self.all_ssr:
            if random.choices([True, False], weights=[ssr.probability, 1-ssr.probability])[0]:
                ssr_val |= 1
                count += ssr.ssr_point
            ssr_val <<= 1
        return ssr_val, count

    def create_passenger(self):
        name = fake.name()
        passenger = None
        with transaction.atomic():
            passenger = Passenger.objects.create(
                name=name,
                email=f"{name}@example.com",
                phone_no='+91' + str(random.randint(1000000000, 9999999999)),
            )
            passenger.save()
        return passenger

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            return

        self.populate_PNR()
