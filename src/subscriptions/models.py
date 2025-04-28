import helpers.billing
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.urls import reverse

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
    description = models.TextField(null=True, blank=True, help_text="Description of the subscription plan")
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, blank=True, related_name="subscriptions")
    permission = models.ManyToManyField(Permission, blank=True, related_name="subscriptions", limit_choices_to={"content_type__app_label": "subscriptions", "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]})
    paddle_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=1, help_text="Ordering on Django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on Django pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(null=True, blank=True, help_text="Features of the subscription plan")

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        ordering = ["order", "featured", "-updated"]
        verbose_name = "Subscription"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.paddle_id:
            paddle_id = helpers.billing.create_product(
                raw=False,
                name=self.name,
                metadata={
                    "subscription_plan_id": self.id,
                    "subscription_plan_name": self.name
                }
            )
            self.paddle_id = paddle_id
        super().save(*args, **kwargs)

    def get_features_list(self):
        return [x.strip() for x in self.features.split("\n")] if self.features else []
    
class SubscriptionPrice(models.Model):

    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, blank=True, null=True, related_name="prices")
    paddle_id = models.CharField(max_length=255, null=True, blank=True)
    interval = models.CharField(max_length=255, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00, help_text="Price of the subscription plan and remove decimal places when updating or creating a price")
    order = models.IntegerField(default=1, help_text="Ordering on Django pricing page")
    featured = models.BooleanField(default=True, help_text="Featured on Django pricing page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["subscription__order", "order", "featured", "-updated"]

    @property
    def get_checkout_url(self):
        return reverse("product_price_redirect", kwargs= {"price_id": self.id})

    @property
    def display_description(self):
        return self.subscription.description if self.subscription.description else "This subscription plan is still in the development pharse and is coming soon."

    @property
    def get_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_list()

    @property
    def display_sub_name(self):
        return self.subscription.name if self.subscription.name else "Plan"

    @property
    def product_paddle_id(self):
        if not self.subscription:
            return None
        return self.subscription.paddle_id
    
    @property
    def paddle_currency(self):
        return "USD"
    
    def __str__(self):
        return self.subscription.name
    
    def save(self, *args, **kwargs):
        if (not self.paddle_id and self.product_paddle_id is not None):
            paddle_id = helpers.billing.create_price(
                raw=False,
                product_id=self.product_paddle_id,
                amount=self.price,
                currency_code=self.paddle_currency,
                interval=self.interval,
                desc=self.subscription.name,
                metadata={
                    "subscription_plan_id": self.subscription.id,
                    "subscription_plan_name": self.subscription.name
                }
            )
            self.paddle_id = paddle_id
        super().save(*args, **kwargs)

        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval,
            ).exclude(id=self.id)
            qs.update(featured=False)

class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CANCELLED = "canceled", "Canceled"
    PAST_DUE = "past_due", "Past Due"
    PAUSED = "paused", "Paused"
    TRIALING = "trialing", "Trialing"

class UserSubscription(models.Model):
    # FIELDS
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, related_name="user_subscription", null=True, blank=True)
    paddle_id = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    starts_at = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    ends_at = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    status = models.CharField(max_length=50, choices=SubscriptionStatus.choices, help_text="Status of the subscription plan", null=True, blank=True)

    def get_absolute_url(self):
        return reverse("billing_details")
    
    @property
    def is_active_status(self):
        return self.status in [
            SubscriptionStatus.ACTIVE, 
            SubscriptionStatus.TRIALING,
            ]
    
    # @property
    # def plan_name(self):
    #     if not self.subscription.name:
    #         return None
    #     return self.subscription.name

    # def serialize(self):
    #     return {
    #         "plan_name": self.plan_name,
    #         "status": self.status,
    #         "starts_at": self.starts_at,
    #         "ends_at": self.ends_at,
    #     }

    def save(self, *args, **kwargs):
        if (self.started_at is None and self.starts_at is not None):
            self.started_at = self.starts_at
        super().save(*args, **kwargs)


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