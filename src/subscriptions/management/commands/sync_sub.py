from typing import Any
from django.core.management.base import BaseCommand

from subscriptions import utils as sub_utils

class Command(BaseCommand):
    help = "Sync subscription permissions and groups"

    def handle(self, *args: Any, **options: Any) -> None:
        sub_utils.sync_subs_group_permissions()