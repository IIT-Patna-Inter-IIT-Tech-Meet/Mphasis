import json
import pytz
import uuid
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import Passenger, Flight, PNR, PassengerSeat, CabinType, ClassType

from faker import Faker
import random
fake = Faker()

NUM_PASSENGERS = int(1e3)

class Command(BaseCommand):
    help = "populate passengers and the pnr tables\n--clean: clear the passengers and pnr tables"
    
        
    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

        parser.add_argument(
            "--pcount",
            default=NUM_PASSENGERS,
            type=int,
            help="populate passengers",
        )
        
    def clean(self):
        with transaction.atomic():
            PNR.objects.all().delete()
            Passenger.objects.all().delete()
        print("Cleaned")
    
    def populate_passengers(self, pcount):
        for _ in range(pcount):
            passenger = Passenger.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_no=fake.phone_number(),
                email=fake.email(),
            )
            passenger.save()
            print("Passenger added : ", passenger)
    
    def populate_PNR(self):
        
        passenger_ids = list(Passenger.objects.values_list('id', flat=True))
        # print(passenger_ids)
        while len(passenger_ids) > 0:
            flight = Flight.objects.order_by('?').first()

            # Check if there are enough passengers to sample
            num_passengers_to_sample = random.randint(1, min(4, len(passenger_ids)))
            sample_passenger_ids = random.sample(passenger_ids, num_passengers_to_sample)

            passenger_ids = [p for p in passenger_ids if p not in sample_passenger_ids]

            pnr = PNR.objects.create(
                flight=flight,
                timestamp=datetime.now(),
                seat_currency='INR',
            )
            pnr.save()
            # Create PassengerSeats and associate them with the created PNR
            for passenger_id in sample_passenger_ids:
                # try:
                #     passenger_seat = PassengerSeat.objects.get(passenger_id=passenger_id, pnr__isnull=True)
                # except PassengerSeat.DoesNotExist:
                #     print(f"PassengerSeat for passenger ID {passenger_id} does not exist or is already associated with a PNR.")
                #     continue
                price = float(random.choice(range(10000, 50000)))
                class_type = ClassType.objects.order_by('?').first()
                cabin = CabinType.objects.order_by('?').first()
                
                passenger_seat = PassengerSeat.objects.create(
                    passenger=Passenger.objects.get(id = passenger_id),
                    ssr = random.choice(random.choice([ssr[0] for ssr in passenger_seat.ssr_types])) if random.randint(1, 100) == 1 else None,
                    paid_service = True if random.randint(1, 100) == 1 else False,
                    loyalty_program = True if random.randint(1, 100) == 1 else False,
                    seat_number =  f"{class_type}--{cabin}--{random.choice(range(1, 1000))}",
                    seat_class = class_type,
                    seat_cabin = cabin,
                    seat_price = price,
                    seat_tax = price*random.choice([0.1, 0.2, 0.3, 0.4]),
                    pnr = pnr,
                )


                # Save the PassengerSeat
                passenger_seat.save()
            pnr.save()
            print(f"created pnr {pnr}")

                
    def handle(self, *args, **options):
        
        if(options['clean']):
            self.clean()
            return
        
        self.populate_passengers(options["pcount"])
        self.populate_PNR()
            