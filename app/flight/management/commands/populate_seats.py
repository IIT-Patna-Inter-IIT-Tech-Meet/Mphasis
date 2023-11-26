import json
import pytz
import uuid
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import CabinType, ClassType, Aircraft, SeatDistribution, Group, SSR
import random
import pandas as pd

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
        df_cabin = pd.read_csv("flight/management/data/cabin.csv")
        df_class = pd.read_csv("flight/management/data/class.csv")
        df_ssr = pd.read_csv("flight/management/data/ssr.csv")
        df_group = pd.read_csv("flight/management/data/group.csv")
        
        for _ in range(len(df_cabin)):
            try:
                cabin_type = CabinType.objects.get(type_name=df_cabin["abb"][_])
            except CabinType.DoesNotExist:
                cabin_type = CabinType.objects.create(
                    type_name=df_cabin["abb"][_],
                    des=df_cabin["des"][_],
                    score=df_cabin["score"][_],
                )
                print(f"added cabin instance {cabin_type}")
        
        for _ in range(len(df_class)):
            try: 
                class_type = ClassType.objects.get(type_name=df_class["abb"][_])
            except ClassType.DoesNotExist:
                class_type = ClassType.objects.create(
                    type_name=df_class["abb"][_],
                    des=df_class["des"][_],
                    score=df_class["score"][_],
                )
                print(f"added class instance {class_type}")
        
        for _ in range(len(df_ssr)):
            try:
                ssr_type = SSR.objects.get(ssr_name=df_ssr["abb"][_])
            except SSR.DoesNotExist:
                ssr_type = SSR.objects.create(
                    ssr_name=df_ssr["abb"][_],
                    ssr_des=df_ssr["des"][_],
                    ssr_point=df_ssr["score"][_],
                )
                print(f"added ssr instance {ssr_type}")
                
        for _ in range(len(df_group)):
            try:
                group_type = Group.objects.get(group_name=df_group["abb"][_])
            except Group.DoesNotExist:
                group_type = Group.objects.create(
                    group_name=df_group["abb"][_],
                    group_des=df_group["des"][_],
                    group_point=df_group["score"][_],
                )
                print(f"added group instance {group_type}")
                
            
    def populate_seat_distribution(self):
        aircraft_list = Aircraft.objects.all()
        dist = [[5, 10, 15], [25, 50, 75], [50, 100, 200]]
        i=0
        j=0
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
                        seats_count = random.choice([50, 100, 200]) # ! need a realistic distribution 
                        if i<3 and j<3:
                            seats_count = dist[i][j]
                        seat_distribution = SeatDistribution.objects.create(
                            aircraft_id=aircraft,
                            class_type=class_type,
                            cabin_type=cabin_type,
                            seat_count=seats_count,
                            seat_avail=seats_count
                        )
                        seat_distribution.save() 
                        print(f"created cabin instance {seat_distribution}")
                    j+=1
                i+=1
        
            
    def handle(self, *args, **options):
        
        if(options['clean']):
            self.clean()
            return
        
        self.populate_basics()
        self.populate_seat_distribution()