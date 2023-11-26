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
        
        pass

                
    def handle(self, *args, **options):
        
        if(options['clean']):
            self.clean()
            return
        
        self.populate_passengers(options["pcount"])
        self.populate_PNR()
            