import json
import pytz
import uuid
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import CabinType, ClassType, Aircraft, SeatDistribution
import random

class Command(BaseCommand):
    help = "Populate Seats data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )
        
    def clean(self):
        with transaction.atomic():
            SeatDistribution.objects.all().delete()
        print("Cleaned")
    
    def populate_basics(self):
        class_types = ['A', 'C', 'K']
        cabin_types = ['F', 'J', 'Y']

        for i in range(3):
            try:
                class_type = ClassType.objects.get(
                    type_name=class_types[i],
                )
            except ClassType.DoesNotExist:
                class_type = ClassType.objects.create(
                    type_name=class_types[i],
                )
                class_type.save()
                print(f"created class instance {class_type}")

            try:
                cabin_type = CabinType.objects.get(
                    type_name=cabin_types[i],
                )
            except CabinType.DoesNotExist:
                cabin_type = CabinType.objects.create(
                    type_name=cabin_types[i],
                )
                cabin_type.save()
                print(f"created cabin instance {cabin_type}")
            
    def populate_seat_distribution(self):
        aircraft_list = Aircraft.objects.all()

        for aircraft in aircraft_list:
            class_types = ClassType.objects.all()
            cabin_types = CabinType.objects.all()
            for class_type in class_types:
                for cabin_type in cabin_types:
                    try:
                        seat_distribution = SeatDistribution.objects.get(
                            aircraft_id=aircraft,
                            class_type=class_type,
                            cabin_type=cabin_type,
                        )
                    except SeatDistribution.DoesNotExist:                        
                        seats_count = random.choice([50, 100, 200])
                        seat_distribution = SeatDistribution.objects.create(
                            aircraft_id=aircraft,
                            class_type=class_type,
                            cabin_type=cabin_type,
                            seat_count=seats_count,
                            seat_avail=seats_count
                        )
                        seat_distribution.save() 
                        print(f"created cabin instance {seat_distribution}")
        
            
    def handle(self, *args, **options):
        
        if(options['clean']):
            self.clean()
            return
        
        self.populate_basics()
        self.populate_seat_distribution()