from io import StringIO
import pytz
import uuid
import random
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import (
    PNR,
    PnrFlightMapping,
    PnrPassenger,
    Flight,
    SeatDistribution,
    Group,
)
from faker import Faker
from app.config import settings

TIME_ZONE = "Asia/Kolkata"
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

        def helper(flight):
            seats = sd[flight.schedule.schedule.aircraft_id]
            total_seats = flight.schedule.schedule.aircraft_id.total_capacity

            # closer the departure date, more the passengers
            days = (flight.departure - datetime.now(pytz.timezone(TIME_ZONE))).days
            if days < 0:
                days = 0
            
            max_limit = max(100 - days*2, 0)

            tofill = (total_seats * random.randint(max_limit - 20, max_limit)) // 100
            for seat in seats:
                if tofill <= 0:
                    break

                if seat.seat_count <= 0:
                    continue

                c = seat.seat_count - random.randint(0, seat.seat_count * 2 // 5)
                while c > 0:
                    tofill = random.randint(
                        1, min(5, c)
                    )  # TODO : need to add some probability distribution
                    c -= tofill

                    # maintain unique
                    id = str(uuid.uuid4())[:6]
                    while id in all_pnr:
                        id = str(uuid.uuid4())[:6]
                    all_pnr.add(id)

                    paid_service = random.random()
                    if paid_service < settings["paid_service"]:
                        paid_service = True
                    else:
                        paid_service = False

                    lp = random.random()
                    if lp < settings["loyality_program"]:
                        lp = True
                    else:
                        lp = False

                    values = [0,1,2,3,4,5]
                    weights = [0.5, 0.2, 0.1, 0.1, 0.05, 0.05]
                    total_ssr = random.choices(values, weights=weights)[0]

                    t = total_ssr // tofill
                    ssrs = [t]*tofill
                    x = total_ssr - t
                    while x > 0:
                        ssrs[random.randint(0, tofill-1)] += 1
                        x -= 1

                    score = (
                        seat.class_type.score
                        + (settings["paid_service_score"] if paid_service else 0)
                        + (settings["loyality_program_score"] if lp else 0)
                        + tofill*int(settings["pax_score"])
                        + total_ssr*int(settings["ssr_score"])
                    )

                    pnr = PNR(
                        pnr=id,
                        seat_class=seat.class_type,
                        paid_service=paid_service,
                        loyalty_program=lp,
                        conn=0,
                        pax=tofill,
                        booking_type=random.choice(all_booking_types),
                        score=score,
                    )
                    self.pnrs.append(pnr)
                    
                    # create pnr_flight_mapping
                    pnr_flight_mapping = PnrFlightMapping(
                        pnr=pnr,
                        flight=flight,
                    )
                    self.pnr_flight_mappings.append(pnr_flight_mapping)

                    for x in range(tofill):
                        # create passenger and add to pnr
                        p = PnrPassenger(
                            recloc = pnr,
                            last_name = fake.last_name(),
                            first_name = fake.first_name(),
                            contact_email = fake.email(),
                            ssr = ssrs[x]
                        )

                        self.pnr_passengers.append(p)
        # bulk fetch
        seat_distributions = SeatDistribution.objects.all()
        all_booking_types = Group.objects.all()

        all_pnr = set()
        sd = {}
        for seat in seat_distributions:
            if seat.aircraft_id not in sd:
                sd[seat.aircraft_id] = []
            sd[seat.aircraft_id].append(seat)

        flights = Flight.objects.all().order_by("departure")
        flight_count = 0
        for flight in flights:
            flight_count += 1
            helper(flight)

            if len(self.pnrs) % 100 == 0:
                print(f"flight count : {flight_count}")
                print(f"pnr count : {len(self.pnrs)}")
                print(f"pnr-flight mapping : {len(self.pnr_flight_mappings)}")
                print(f"pnr-passenger : {len(self.pnr_passengers)}")

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            # return

        self.populate_PNR()
        print("Populating PNR, PNRFlightMapping, PnrPassenger")
        with transaction.atomic():
            PNR.objects.bulk_create(self.pnrs)
            PnrFlightMapping.objects.bulk_create(self.pnr_flight_mappings)
            PnrPassenger.objects.bulk_create(self.pnr_passengers)
        print(f"PNR populated with {len(self.pnrs)} entries")
        print(f"PNRFlightMapping populated with {len(self.pnr_flight_mappings)} entries")
        print(f"PnrPassenger populated with {len(self.pnr_passengers)} entries")