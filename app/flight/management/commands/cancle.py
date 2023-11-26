from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Flight

class Command(BaseCommand):
    help = "Randomly cancels x% of the flights"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--percent",
            type=float,
            default=0.05,
            help="Percentage of flights to cancel",
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        percent = options["percent"]
        if percent < 0 or percent > 1:
            print("Invalid percentage")
            return

        flights = Flight.objects.all()
        num_flights = len(flights)
        num_cancelled = int(num_flights * percent)

        print(f"Cancelling {num_cancelled} flights out of {num_flights} flights")

        for flight in flights.order_by("?")[:num_cancelled]:
            flight.status = "red"
            flight.save()

        print("Done")