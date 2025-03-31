from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, blank=True, related_name="subscriptions")

    class Meta:
        permissions = [
            ("advanced", "Advanced Permission"),
            ("pro", "Pro Permission"),
            ("basic", "Basic Permission"),
        ]
