from typing import Any
from django.core.management.base import BaseCommand

from subscriptions import utils as sub_utils

class Command(BaseCommand):
    help = "Sync user subscriptions with Paddle"

    def add_arguments(self, parser):
        parser.add_argument("--clear-inactive-subscriptions", action="store_true", default=False)
        parser.add_argument("--days-left", default=0, type=int)
        parser.add_argument("--days-ago", default=0, type=int)
        parser.add_argument("--day-start", default=0, type=int)
        parser.add_argument("--day-end", default=0, type=int)


    def handle(self, *args: Any, **options: Any):
        days_left = options.get("days_left")
        days_ago = options.get("days_ago")
        day_start = options.get("day_start")
        day_end = options.get("day_end")
        clear_subs = options.get("clear_subs")
        if clear_subs:
            sub_utils.clear_inactive_subs()
        else:
            print("Sync active subscriptions")
            done =  sub_utils.refresh_users_subs(active_only=True, verbose=True, days_ago=days_ago, days_left=days_left, day_start=day_start, day_end=day_end)
            if done:
                print("Done")