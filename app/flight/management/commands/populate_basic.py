from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import CabinType, ClassType, Group, SSR, Carrier
import pandas as pd


class Command(BaseCommand):
    help = "Populate Cabin Types, Class Types, SSRs, Groups\n--clean: clear the tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

    @staticmethod
    def clean():
        with transaction.atomic():
            CabinType.objects.all().delete()
            ClassType.objects.all().delete()
            SSR.objects.all().delete()
            Group.objects.all().delete()
            Carrier.objects.all().delete()

        print("Cleaned Cabin Types, Class Types, SSRs, Groups")

    @staticmethod
    def populate_basics():
        df_cabin = pd.read_csv("flight/management/data/cabin.csv")
        df_class = pd.read_csv("flight/management/data/class.csv")
        df_ssr = pd.read_csv("flight/management/data/ssr.csv")
        df_group = pd.read_csv("flight/management/data/group.csv")
        df_carreir = pd.read_csv("flight/management/data/carrier.csv")

        # populating Cabin Type table
        cabins = []
        for i in range(len(df_cabin)):
            try:
                cabin_type = CabinType.objects.get(type_name=df_cabin["abb"][i])
            except CabinType.DoesNotExist:
                cabin_type = CabinType(
                    type_name=df_cabin["abb"][i],
                    des=df_cabin["des"][i],
                    score=df_cabin["score"][i],
                )
                cabins.append(cabin_type)

        if len(cabins) > 0:
            CabinType.objects.bulk_create(cabins)
        print(f"Added {len(cabins)} cabin instances.")

        # populating Class Type table
        classes = []
        for i in range(len(df_class)):
            try:
                class_type = ClassType.objects.get(type_name=df_class["abb"][i])
            except ClassType.DoesNotExist:
                cabin = CabinType.objects.get(type_name=df_class["cabin"][i])
                class_type = ClassType(
                    type_name=df_class["abb"][i],
                    des=df_class["des"][i],
                    score=df_class["score"][i],
                    cabin=cabin,
                )
                classes.append(class_type)

        if len(classes) > 0:
            ClassType.objects.bulk_create(classes)
        print(f"Added {len(classes)} class instance.")

        # populating SSR table
        ssrs = []
        for i in range(len(df_ssr)):
            try:
                ssr_type = SSR.objects.get(ssr_name=df_ssr["abb"][i])
            except SSR.DoesNotExist:
                ssr_type = SSR(
                    ssr_name=df_ssr["abb"][i],
                    ssr_des=df_ssr["des"][i],
                    ssr_point=df_ssr["score"][i],
                    probability=df_ssr["prob"][i],
                )
                ssrs.append(ssr_type)

        if len(ssrs) > 0:
            SSR.objects.bulk_create(ssrs)
        print(f"Added {len(ssrs)} ssr instance.")

        # populating Group table
        groups = []
        for i in range(len(df_group)):
            try:
                group_type = Group.objects.get(group_name=df_group["abb"].iloc[i])
            except Group.DoesNotExist:
                group_type = Group(
                    group_name=df_group["abb"].iloc[i],
                    group_des=df_group["des"].iloc[i],
                    group_point=df_group["score"].iloc[i],
                )
                groups.append(group_type)

        if len(groups) > 0:
            Group.objects.bulk_create(groups)
        print(f"Added {len(groups)} group instance.")

        # populating Carrier table
        carriers = []
        for i in range(len(df_carreir)):
            try:
                carrier_type = Carrier.objects.get(code=df_carreir["code"].iloc[i])
            except Carrier.DoesNotExist:
                carrier_type = Carrier(
                    code=df_carreir["code"].iloc[i],
                    desc=df_carreir["desc"].iloc[i],
                )
                carriers.append(carrier_type)
        Carrier.objects.bulk_create(carriers)
        print(f"Added {len(carriers)} carrier instance.")

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            # return

        self.populate_basics()
