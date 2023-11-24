import json
import pytz
import uuid
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand
from flight.models import Airport, Aircraft, Flight

TIME_ZONE = "Asia/Kolkata"

class Command(BaseCommand):
    help = "Populate flight data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            help="clean table before populating",
        )

    def clean(self):
        with transaction.atomic():
            Flight.objects.all().delete()
            Aircraft.objects.all().delete()
        print("Cleaned")

    def handle(self, *args, **options):
        if options["clean"]:
            self.clean()
            return

        for data in loadjson():
            dst_iatacode = data["result"]["request"]["code"]
            dst = Airport.objects.get(iata_code = dst_iatacode)

            try:
                sources = data["result"]["response"]["airport"]["pluginData"]["schedule"]["arrivals"]["data"]
            except:
                sources = []
            # print(sources[0].keys())
            for source in sources:
                try:
                    if source is None: continue
                    aircraft_reg = source.get("flight", {}).get("aircraft", {}).get("registration", None)
                    if aircraft_reg is None: continue
                except:
                    print("Error in source : ", source)
                    continue
                try:
                    aircraft = Aircraft.objects.get(registration = aircraft_reg)
                except Aircraft.DoesNotExist:
                    print("Aircraft not found. Adding new aircraft . . .")

                    try:
                        owner_code = f'{source["flight"]["owner"]["code"]["iata"]} +  {source["flight"]["owner"]["code"]["icao"]}',
                        owner_name = source["flight"]["owner"]["name"],
                    except:
                        owner_code = " "
                        owner_name = " "

                    aircraft = Aircraft.objects.create(
                        registration = aircraft_reg,
                        model = source["flight"]["aircraft"]["model"]["code"],
                        name = source["flight"]["aircraft"]["model"]["text"],
                        owner_code = owner_code[0],
                        owner_name = owner_name[0],
                    )
                    aircraft.save()
                    print("Aircraft added : ", aircraft)
                except Exception as e:
                    print(e)
                    continue
                # check if source exists
                origin = source["flight"]["airport"]["origin"]["code"]["iata"]
                try:
                    source_airport = Airport.objects.get(iata_code = origin)
                except Airport.DoesNotExist:
                    # can't add
                    source_airport = None
                if source_airport is None:
                    continue
                    
                flight_id = source["flight"]["identification"]["id"]
                if flight_id is None:
                    flight_id = f'{source["flight"]["identification"]["number"]["default"]}-{source["flight"]["time"]["scheduled"]["departure"]}'
                try:
                    flight = Flight.objects.get(id = flight_id)
                    print("Flight already exists : ", flight)
                except Flight.DoesNotExist:
                    flight = Flight.objects.create(
                        id = flight_id,
                        flight_number = source["flight"]["identification"]["number"]["default"],
                        aircraft_id = aircraft,
                        departure_airport_id = source_airport,
                        arrival_airport_id = dst,
                        departure_time = datetime.fromtimestamp(source["flight"]["time"]["scheduled"]["departure"],tz=pytz.timezone(TIME_ZONE)),
                        arrival_time = datetime.fromtimestamp(source["flight"]["time"]["scheduled"]["arrival"], tz=pytz.timezone(TIME_ZONE)),
                        flight_time = int(source["flight"]["time"]["scheduled"]["arrival"]) - int(source["flight"]["time"]["scheduled"]["departure"]),
                        status = "green",
                    )
                    flight.save()
                    print("Flight added : ", flight)
                except Exception as e:
                    print(e, flight_id)
                    continue
            # create flight
        print("Done")
        

def loadjson():
    all_codes = ['gop', 'ixi', 'pbd', 'ixu', 'ltu', 'rgh', 'vtz', 'myq', 'rrk', 'bep', 'ixq', 'gux', 'ktu', 'ixe', 'rmd', 'ixy', 'hyd', 'gay', 'jga', 'nvy', 'cbd', 'tni', 'rew', 'ixc', 'ixm', 'jlr', 'agx', 'pyb', 'ixd', 'jrh', 'amd', 'vga', 'bek', 'ixz', 'jsa', 'rup', 'bho', 'pnq', 'ixx', 'hsr', 'lko', 'maa', 'dbr', 'blr', 'nag', 'tir', 'ixr', 'rdp', 'sag', 'kqh', 'mzu', 'raj', 'pat', 'put', 'ixk', 'gbi', 'ixp', 'dgh', 'ixj', 'aip', 'pgh', 'imf', 'shl', 'jai', 'pny', 'dib', 'ixa', 'trv', 'sse', 'ajl', 'hss', 'bpm', 'diu', 'bhu', 'dhm', 'del', 'udr', 'ixb', 'tez', 'sxr', 'bbi', 'hjr', 'gox', 'hbx', 'omn', 'cnn', 'cjb', 'stv', 'cok', 'ixg', 'ixs', 'tei', 'bhj', 'ixh', 'bup', 'gwl', 'idr', 'klh', 'wgc', 'bkb', 'bom', 'jdh', 'dbd', 'atq', 'rtc', 'ded', 'goi', 'rja', 'knu', 'trz', 'isk', 'pab', 'ixl', 'ccj', 'kuu', 'hgi', 'sdw', 'bdq', 'akd', 'coh', 'sxv', 'agr', 'kjb', 'dep', 'ixt', 'ixw', 'vns', 'pyg', 'rpr', 'luh', 'ccu', 'slv', 'lda', 'jrg', 'tcr', 'ixn', 'gdb', 'cdp', 'gau', 'ndc', 'ixv', 'nmb', 'zer', 'rji', 'vdy', 'dmu', 'kbk', 'tjv', 'jgb']
    for code in all_codes:
        filepath = f"flight/management/data/routes/data/arrival_{code}.json"
        with open(filepath, "r") as f:
            data = json.load(f)
        yield data

