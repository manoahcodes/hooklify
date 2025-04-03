from typing import Any
from django.core.management.base import BaseCommand

from subscriptions.models import Subscription

class Command(BaseCommand):
    help = "Sync subscription permissions and groups"

    def handle(self, *args: Any, **options: Any) -> None:
        # Get all subscriptions
        qs = Subscription.objects.filter(active=True)
        for obj in qs:
            # print(obj.groups.all())
            sub_perms = obj.permission.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)
                # for perm in obj.permission.all():
                #     group.permissions.add(perm)
            # print(obj.permission.all())