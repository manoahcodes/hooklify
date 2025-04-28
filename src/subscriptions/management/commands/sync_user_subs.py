from typing import Any
from django.core.management.base import BaseCommand

from subscriptions import utils as sub_utils

class Command(BaseCommand):
    help = "Sync user subscriptions with Paddle"

    def add_arguments(self, parser):
        parser.add_argument("--clear-inactive-subscriptions", action="store_true", default=False)

    def handle(self, *args: Any, **options: Any):
        clear_subs = options.get("clear_subs")
        if clear_subs:
            sub_utils.clear_inactive_subs()
        else:
            print("Sync active subscriptions")
            print("Done")