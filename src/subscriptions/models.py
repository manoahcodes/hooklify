from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save

from django.conf import settings

User = settings.AUTH_USER_MODEL

SUBSCRIPTION_PERMISSIONS = [
    ("premium", "Advanced Permission"),
    ("super premium", "Super Advanced Permission"),
    ("pro", "Pro Permission"),
    ("basic", "Basic Permission"),
]

ALLOW_CUSTOM_GROUPS = True

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, blank=True, related_name="subscriptions")
    permission = models.ManyToManyField(Permission, blank=True, related_name="subscriptions", limit_choices_to={"content_type__app_label": "subscriptions", "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]})
    
    def __str__(self):
        return self.name

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        verbose_name = "Subscription Options"

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, related_name="user_subscription", null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription.name}" if self.subscription else self.user.username

def user_sub_post_save(sender, instance, created, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    sub_obj = user_sub_instance.subscription
    groups_ids = []
    if sub_obj is not None:
        groups = sub_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if sub_obj is not None:
            subs_qs = subs_qs.exclude(id=sub_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        curnt_groups = user.groups.all().values_list("id", flat=True)
        group_id_set = set(groups_ids)
        curnt_group_id_set = set(curnt_groups) - subs_groups_set
        final_group_ids = list(group_id_set | curnt_group_id_set)
        user.groups.set(final_group_ids)

post_save.connect(user_sub_post_save, sender=UserSubscription)