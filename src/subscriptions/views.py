from django.shortcuts import render
from django.urls import reverse
from subscriptions.models import SubscriptionPrice

# Create your views here.
def subscription_price_view(request, interval="month"):
    qs = SubscriptionPrice.objects.filter(featured=True)
    inv_mon = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_year = SubscriptionPrice.IntervalChoices.YEARLY
    object_list = qs.filter(interval=inv_mon)
    url_path_name = "pricing_interval"
    mo_url = reverse(url_path_name, kwargs={"interval": inv_mon})
    yr_url = reverse(url_path_name, kwargs={"interval": inv_year})
    active = inv_mon
    if interval == inv_year:
        active = inv_year
        object_list = qs.filter(interval=inv_year)
    return render(request, "subscriptions/pricing.html", {
        "object_list": object_list,
        "mo_url": mo_url,
        "yr_url": yr_url,
        "active": active,
    })