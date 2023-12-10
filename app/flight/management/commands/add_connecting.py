from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import  PNR

class Command(BaseCommand):
    help = "Randomly addes connecting flights to 'X' no of pnr"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--count",
            type=float,
            default=0.001,
            help="Percentage of flights to cancel",
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        pnrs = PNR.objects.order_by('?')[:options["count"]]
        