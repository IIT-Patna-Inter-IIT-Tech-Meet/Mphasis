import datetime
from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Flight

class Command(BaseCommand):
    help = "Undo all the cancelled flights"

    def handle(self, *args: Any, **options: Any) -> str | None:
        Flight.objects.filter(status = "Cancelled").update(status="Scheduled")
        print("Done")