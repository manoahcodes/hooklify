import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from subscriptions.models import SubscriptionPrice, UserSubscription
from subscriptions import utils as subs_utils


@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)

    if request.method == "POST":
        finished = subs_utils.refresh_users_subs(user_ids=[request.user.id], active_only=False)
        if finished:
            messages.success(request, "Your subscription has been updated.")
        else:
            messages.error(request, "There was an error updating your subscription.")
        return redirect(user_sub_obj.get_absolute_url())

    return render(request, "subscriptions/user_details.html", {"subscription": user_sub_obj})


@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if user_sub_obj.paddle_id and user_sub_obj.is_active_status:
            # Only trigger the Paddle cancel API
            helpers.billing.cancel_old_subscription(user_sub_obj.paddle_id, raw=False)

            messages.success(request, "Your subscription has been cancelled.")
        else:
            messages.error(request, "Your subscription is already cancelled or does not exist.")
        return redirect(user_sub_obj.get_absolute_url())

    return render(request, "subscriptions/user_cancel_details.html", {"subscription": user_sub_obj})


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
    return render(
        request,
        "subscriptions/pricing.html",
        {
            "object_list": object_list,
            "mo_url": mo_url,
            "yr_url": yr_url,
            "active": active,
        },
    )
