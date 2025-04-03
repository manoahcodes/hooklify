from django.contrib import admin
from .models import Subscription, UserSubscription

# Register your models here.
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["groups"]
    # fields = ["name", "groups"]

admin.site.register(Subscription)
admin.site.register(UserSubscription)
