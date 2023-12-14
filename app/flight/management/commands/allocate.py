from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Flight
from app.config import load_settings
from flight.core.allocation import PnrReallocation
from flight.utils import util_flight_ranking, util_pnr_ranking, cancelled_flight


class Command(BaseCommand):
    help = "Allocates alternate flights for cancelled flights"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--config",
            type=str,
            default="settings.yml",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def wrapper_flight_ranking(self):
        # def util_flight_ranking(flight_id, max_hop=2, use_inventory=False, use_cabin_only=True, neighboring_search=True):
        def callable_function(flight_id):
            return util_flight_ranking(
                flight_id,
                max_hop=self.config["search"]["max_hop"],
                use_inventory=self.config["search"]["use_inventory"],
                use_cabin_only=self.config["search"]["use_cabin_only"],
                neighboring_search=self.config["search"]["neighboring_search"],
            )

        return callable_function

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.config = load_settings(options["config"])

        fn_flight_ranking = self.wrapper_flight_ranking(self)
        self.allocator = PnrReallocation(
            get_alt_flights_fn=fn_flight_ranking,
            get_pnr_fn=util_pnr_ranking,
            get_cancled_fn=cancelled_flight,
        )

        result = self.allocator.allocate()
        print(result)


