from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from webhook.views import paddle_transaction_webhook_view

from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from customers.models import Customer

# Create your views here.
def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect("paddle_checkout_start")

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
    # print("checkout_subscription_price_id", checkout_subscription_price_id)
    if checkout_subscription_price_id is None or obj is None:
        return redirect("pricing")
    # customer_paddle_id = request.user.customer.paddle_id
    return redirect(f"/checkout/{obj.paddle_id}/")

@login_required
def checkout_start_view(request, checkout_subscription_price_id, *args, **kwargs):
    # Retrieve subscription price ID from the session
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    if not checkout_subscription_price_id:
        return redirect("pricing")
    
    # Get the customer's Paddle ID from the Customer model
    customer = Customer.objects.filter(user=request.user).first()
    if not customer or not customer.paddle_id:
        return redirect("pricing")
    
    # Get the subscription price object
    price_obj = SubscriptionPrice.objects.filter(id=checkout_subscription_price_id).first()
    if not price_obj:
        return redirect("pricing")
    
    product = Subscription.objects.filter(id=price_obj.subscription.id).first()
    if not product:
        return redirect("pricing")
    
    # Calculate product price and total (since digital products require no shipping)
    product_name = product.name
    product_price = price_obj.price           # assuming a Decimal field
    total = product_price
    
    # Build the success and cancel URLs using Django's reverse
    cancel_url = reverse("pricing")
    success_url = reverse("pending_checkout")
    
    # Prepare the context for the checkout template
    context = {
        "price_id": price_obj.paddle_id,
        "customer_id": customer.paddle_id,
        "cancel_url": cancel_url,
        "success_url": success_url,
        "product_name": product_name,
        "product_price": product_price,
        "total": total,
        "hide_navbar": True,
    }
    
    return render(request, "subscriptions/checkout.html", context)

@login_required
def checkout_pending_view(request):
    try:
        user_sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        # The user hasn't started a subscription yet
        return redirect("pricing")

    # Handle case where the subscription object hasn't been linked yet
    if not user_sub.subscription:
        return redirect("pending_checkout")

    # Wait until the webhook activates the subscription
    if user_sub.subscription.active:
        return redirect("paddle_checkout_end")

    return render(request, "subscriptions/pending.html")


@login_required
def checkout_finalize_view(request):
    user_sub = request.user.subscription

    context = {
        "subscription_name": user_sub.subscription.name,
        "subscription_features": user_sub.subscription.get_features_list(),
    }
    return render(request, "subscriptions/success.html", context)