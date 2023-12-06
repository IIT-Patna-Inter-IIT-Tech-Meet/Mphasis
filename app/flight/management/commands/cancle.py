from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Flight

class Command(BaseCommand):
    help = "Randomly cancels x% of the flights"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--percent",
            type=float,
            default=0.001,
            help="Percentage of flights to cancel",
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        percent = options["percent"]
        if percent < 0 or percent > 1:
            print("Invalid percentage")
            return
        c = int(Flight.objects.count())
        num_cancelled = int(c * percent)
        flights = Flight.objects.order_by('?')[:num_cancelled].values_list('flight_id', flat=True)
        Flight.objects.filter(flight_id__in=flights).update(status="Cancelled")
        print(f"Cancelle {num_cancelled} flights out of {c} flights")
