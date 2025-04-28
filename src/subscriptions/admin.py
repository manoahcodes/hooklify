from django.contrib import admin
from .models import Subscription, UserSubscription, SubscriptionPrice

# Register your models here.
class SubscriptionPriceAdmin(admin.TabularInline):
    model = SubscriptionPrice
    extra = 0
    readonly_fields = ('paddle_id', "subscription")
    list_display = ["subscription", "price", "interval"]
    can_delete = False

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPriceAdmin]
    list_display = ["name", "active"]
    readonly_fields = ('paddle_id',)

class UserSubscriptionAdmin(admin.ModelAdmin):
    model = SubscriptionPriceAdmin
    list_display = ["user", "subscription", "active"]
    readonly_fields = ('user', 'subscription','paddle_id', 'active', 'cancelled', 'starts_at', 'ends_at', 'started_at', 'status')

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
admin.site.register(SubscriptionPrice)
