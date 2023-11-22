import json
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        data = loadjson()

def loadjson():
    filepath = "flight/management/data/arrival_data.json"
    with open(filepath, "r") as f:
        data = json.load(f)
    return data
