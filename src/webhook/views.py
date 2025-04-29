# Standard Library
import json

# Django Imports
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Third-Party Imports
from decouple import config
from paddle_billing.Notifications import Secret, Verifier

# Project Imports
from helpers.billing import get_subscription_plan, cancel_old_subscription
from subscriptions.models import SubscriptionPrice, UserSubscription, SubscriptionStatus

# Constants
PADDLE_WEBHOOK_SECRET_TRANSACTIONAL_KEY = config("PADDLE_WEBHOOK_TRANSACTIONAL_SECRET_KEY", default="", cast=str)
PADDLE_WEBHOOK_SECRET_SUBSCRIPTION_KEY = config("PADDLE_WEBHOOK_SUBSCRIPTION_SECRET_KEY", default="", cast=str)

User = get_user_model()


@csrf_exempt
@require_POST
def paddle_transaction_webhook_view(request):
    """Handles Paddle transaction.completed webhook events."""

    # Verify signature
    if not Verifier().verify(request, Secret(PADDLE_WEBHOOK_SECRET_TRANSACTIONAL_KEY)):
        return HttpResponse("Invalid signature", status=400)

    try:
        payload = json.loads(request.body)
        event_type = payload.get("event_type")
        data = payload.get("data", {})

        if event_type != "transaction.completed":
            return JsonResponse({"status": f"Unhandled event type: {event_type}"}, status=200)

        txn_sub_id = data.get("subscription_id")
        if not txn_sub_id:
            return JsonResponse({"error": "No subscription_id found in event"}, status=400)

        # ✅ Fetch subscription info
        subscription_data = get_subscription_plan(txn_sub_id, raw=True)
        if not subscription_data or not hasattr(subscription_data, "items") or not subscription_data.items:
            return JsonResponse({"error": "Invalid subscription data from Paddle"}, status=400)

        price_id = subscription_data.items[0].price.id
        customer_id = subscription_data.customer_id
        billing_period_start = subscription_data.current_billing_period.starts_at
        billing_period_end = subscription_data.current_billing_period.ends_at
        status = subscription_data.status

        # print("status", status)
        # print("billing_period_start", billing_period_start)
        # print("billing_period_end", billing_period_end)

        try:
            sub_item = SubscriptionPrice.objects.get(paddle_id=price_id)
        except SubscriptionPrice.DoesNotExist:
            return JsonResponse({"error": "SubscriptionPrice not found"}, status=404)

        subscription_obj = sub_item.subscription

        try:
            user_obj = User.objects.get(customer__paddle_id=customer_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this Paddle customer ID not found"}, status=404)

        # ✅ Cancel old subscription if it's different
        try:
            existing_sub = UserSubscription.objects.get(user=user_obj)
            if existing_sub.paddle_id and existing_sub.paddle_id != txn_sub_id:
                try:
                    cancel_response = cancel_old_subscription(txn_id=existing_sub.paddle_id)

                    if cancel_response.status == "canceled":
                        JsonResponse({"message": f"Subscription was already canceled:"}, status=200)
                        
                    JsonResponse({"message": f"Canceled old subscription {existing_sub.paddle_id}: {cancel_response}"}, status=200)
                except Exception as cancel_err:
                    JsonResponse({"message": f"Failed to cancel old subscription: {str(cancel_err)}"}, status=500)
        except UserSubscription.DoesNotExist:
            existing_sub = None

        # ✅ Update/create current subscription
        user_sub, _ = UserSubscription.objects.update_or_create(
            user=user_obj,
            defaults={
                "subscription": subscription_obj,
                "paddle_id": txn_sub_id,
                "active": True,
                "cancelled": False,
                "starts_at": billing_period_start,
                "ends_at": billing_period_end,
                "status": status,
            }
        )

        return JsonResponse({"status": "Subscription successfully updated"}, status=200)

    except Exception as e:
        print("Error in Paddle webhook:", str(e))
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def paddle_subscription_cancelled_webhook_view(request):
    """Handles Paddle subscription.canceled webhook events."""

    if not Verifier().verify(request, Secret(PADDLE_WEBHOOK_SECRET_SUBSCRIPTION_KEY)):
        return HttpResponse("Invalid signature", status=400)

    try:
        payload = json.loads(request.body)
        event_type = payload.get("event_type")
        data = payload.get("data", {})

        if event_type != "subscription.canceled":
            return JsonResponse({"status": f"Unhandled event type: {event_type}"}, status=200)

        # 🔍 Extract subscription ID
        txn_sub_id = data.get("id")
        if not txn_sub_id:
            return JsonResponse({"error": "No subscription_id found in event"}, status=400)
        
        subscription_data = get_subscription_plan(txn_sub_id, raw=True)
        if (not subscription_data or not hasattr(subscription_data, "items") or not subscription_data.items):
            return JsonResponse(
                {"error": "Invalid subscription data from Paddle"}, status=400
            )
        
        customer_id = subscription_data.customer_id
        price_id = subscription_data.items[0].price.id

        try:
            sub_item = SubscriptionPrice.objects.get(paddle_id=price_id)
        except SubscriptionPrice.DoesNotExist:
            return JsonResponse({"error": "SubscriptionPrice not found"}, status=404)

        try:
            user_obj = User.objects.get(customer__paddle_id=customer_id)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User with this Paddle customer ID not found"}, status=404
            )
        
        subscription_obj = sub_item.subscription
        status = subscription_data.status

        user_sub, _ =UserSubscription.objects.update_or_create(
            user=user_obj,
            defaults={
                "subscription": subscription_obj,
                "paddle_id": txn_sub_id,
                "active": False,
                "cancelled": True,
                "starts_at": None,
                "ends_at": None,
                "status": status,
            },
        )

        return JsonResponse({"status": "Subscription cancelled and updated."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
