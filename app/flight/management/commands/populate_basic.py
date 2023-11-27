from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import CabinType, ClassType, SeatDistribution, Group, SSR
import pandas as pd

class Command(BaseCommand):
    help = "Populate Cabin Types, Class Types, SSRs, Groups, and Seat Distribution\n--clean: clear the tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )
        
    def clean(self):
        with transaction.atomic():
            CabinType.objects.all().delete()
            ClassType.objects.all().delete()
            SSR.objects.all().delete()
            Group.objects.all().delete()
        print("Cleaned")
    
    def populate_basics(self):
        df_cabin = pd.read_csv("flight/management/data/cabin.csv")
        df_class = pd.read_csv("flight/management/data/class.csv")
        df_ssr = pd.read_csv("flight/management/data/ssr.csv")
        df_group = pd.read_csv("flight/management/data/group.csv")
        
        # populating Cabin Type table
        for i in range(len(df_cabin)):
            try:
                cabin_type = CabinType.objects.get(type_name=df_cabin["abb"][i])
            except CabinType.DoesNotExist:
                cabin_type = CabinType.objects.create(
                    type_name=df_cabin["abb"][i],
                    des=df_cabin["des"][i],
                    score=df_cabin["score"][i],
                )
                print(f"added cabin instance {cabin_type}")
        
        # populating Class Type table
        for i in range(len(df_class)):
            try: 
                class_type = ClassType.objects.get(type_name=df_class["abb"][i])
            except ClassType.DoesNotExist:
                cabin = CabinType.objects.get(type_name=df_class["cabin"][i])
                class_type = ClassType.objects.create(
                    type_name=df_class["abb"][i],
                    des=df_class["des"][i],
                    score=df_class["score"][i],
                    cabin = cabin,
                    upper = df_class["upper"][i],
                    lower = df_class["lower"][i],
                )
                print(f"added class instance {class_type}")
        
        # populating SSR table
        for i in range(len(df_ssr)):
            try:
                ssr_type = SSR.objects.get(ssr_name=df_ssr["abb"][i])
            except SSR.DoesNotExist:
                ssr_type = SSR.objects.create(
                    ssr_name=df_ssr["abb"][i],
                    ssr_des=df_ssr["des"][i],
                    ssr_point=df_ssr["score"][i],
                    probability=df_ssr["probability"][i],
                )
                print(f"added ssr instance {ssr_type}")

        # populating Group table  
        for i in range(len(df_group)):
            try:
                group_type = Group.objects.get(group_name=df_group["abb"][i])
            except Group.DoesNotExist:
                group_type = Group.objects.create(
                    group_name=df_group["abb"][i],
                    group_des=df_group["des"][i],
                    group_point=df_group["score"][i],
                )
                print(f"added group instance {group_type}")
            
    def handle(self, *args, **options):
        
        if(options['clean']):
            self.clean()
            return
        
        self.populate_basics()