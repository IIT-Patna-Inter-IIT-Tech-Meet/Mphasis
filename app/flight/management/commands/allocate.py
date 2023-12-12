from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from flight.models import Flight
from app.config import load_settings

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

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.config = load_settings(options["config"])
        
        