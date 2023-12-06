import json
import pytz
import random
import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import FlightSchedule, FlightScheduleDate, Flight, Carrier, Aircraft, Airport
import uuid

TIME_ZONE = "Asia/Kolkata"
FLIGHT_COUNT_PER_AIRCRAFT = 7

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )
    
    def clean(self):
        with transaction.atomic():
            FlightScheduleDate.objects.all().delete()
            FlightSchedule.objects.all().delete()
            Flight.objects.all().delete()
        print("Cleaned")

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()

        all_carriers = Carrier.objects.all()
        all_aircrafts = Aircraft.objects.all()
        all_airport = Airport.objects.all()
        day_map = {
            "Sunday" : 0,
            "Monday" : 1,
            "Tuesday" : 2,
            "Wednesday" : 3,
            "Thursday" : 4,
            "Friday" : 5,
            "Saturday" : 6,
        }

        # 
        # Populate Flight per aircraft
        flights = []
        flights_schedule = []
        flights_schedule_date = []
        all_fids = set()

        id = 78465
        for aircraft in all_aircrafts:
            count = FLIGHT_COUNT_PER_AIRCRAFT + random.randint(-5, 5)
            for i in range(count):
                src = random.choice(all_airport)
                dst = random.choice(all_airport)
                while src == dst:
                    dst = random.choice(all_airport)

                departure_time = datetime.datetime.now(pytz.timezone(TIME_ZONE))
                random_hour, random_min = random.randint(1, 24), random.randint(1, 60)
                delta = datetime.timedelta(hours=random_hour, minutes=random_min)
                departure_time = departure_time + delta
                delta = datetime.timedelta(hours=random.randint(0,2), minutes=random.randint(1, 60))
                arrival_time = departure_time + delta

                start_date = datetime.date.today() + datetime.timedelta(days=random.randint(-15, 15))
                end_date = start_date + datetime.timedelta(days=random.randint (15, 90))
                
                x = random.randint(1, 2**7 -1 )
                xb = "{0:08b}".format(x)[1:]
                m = list(map(lambda x: True if x == '1' else False, xb))
                f = sum(list(map(int, xb)))

                flight = FlightSchedule(
                    id = f"SCH-ZZ-{id}",
                    aircraft_id=aircraft,
                    carrier_cd=random.choice(all_carriers),
                    departure_airport=src,
                    arrival_airport=dst,
                    departure_time=departure_time.time(),
                    arrival_time=arrival_time.time(),
                    start_date = start_date,
                    end_date = end_date,
                    r_sun=m[0],
                    r_mon=m[1],
                    r_tue=m[2],
                    r_wed=m[3],
                    r_thr=m[4],
                    r_fri=m[5],
                    r_sat=m[6],
                    freq=f,
                    status = "Scheduled"
                )

                flights_schedule.append(flight)
                id += 1

                # add it's schedule date
                # add 10-20 schedule dates
                inr = 0
                today = start_date.strftime("%A")
                delta = day_map[today]
                c = 0
                for j in range(random.randint(10, 20)):
                    c += 1
                    # That day should be true in the schedule
                    # print(m)
                    while not m[delta]:
                        delta = (delta + 1) % 7
                        # print(delta)
                    
                    date = start_date + datetime.timedelta(days=delta)
                    flight_date = FlightScheduleDate(
                        schedule=flight,
                        date=date,
                    )
                    flights_schedule_date.append(flight_date)
                    
                    fid = str(uuid.uuid4())[:8]
                    if fid in all_fids:
                        fid = str(uuid.uuid4())[:8]
                    all_fids.add(fid)

                    f = Flight(
                        flight_id = fid,
                        schedule=flight_date,
                        status = "Scheduled",
                        departure = departure_time,
                        arrival = arrival_time,
                        src = src,
                        dst = dst,
                    )

                    flights.append(f)
                # add it's flights

        print(f"Populating...{len(flights)} flights,{len(flights_schedule)} flights schedule,{len(flights_schedule_date)} flights schedule date ")
        
        FlightSchedule.objects.bulk_create(flights_schedule)
        FlightScheduleDate.objects.bulk_create(flights_schedule_date)
        Flight.objects.bulk_create(flights)
    
        print(f"Populated {len(flights)} flights")
        print(f"Populated {len(flights_schedule)} flights schedule")
        print(f"Populated {len(flights_schedule_date)} flights schedule date")
