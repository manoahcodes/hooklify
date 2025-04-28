import helpers.billing

from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription

def clear_inactive_subs(self):
    qs = Customer.objects.filter(paddle_id__isnull=False)

    for customer_obj in qs:
        user = customer_obj.user
        customer_paddle_id = customer_obj.paddle_id
        print(f"Syncing user {user.username} with Paddle ID {customer_paddle_id}")

        # Get active subscriptions from Paddle
        subs = helpers.billing.get_customer_subscription_plans(customer_paddle_id)

        # Get user's known subscription Paddle IDs from your database
        user_known_paddle_ids = set(
            UserSubscription.objects.filter(user=user)
            .values_list('paddle_id', flat=True)
        )

        for sub in subs:
            sub_id_str = str(sub.id).strip()

            if sub_id_str in user_known_paddle_ids:
                # This subscription is recorded in the database for this user
                continue

            # Subscription is not recorded — cancel it
            helpers.billing.cancel_old_subscription(sub.id, raw=False)
            print(f"Canceled unknown subscription: {sub.id} for user {user.username}")
            

def sync_subs_group_permissions():
    qs = Subscription.objects.filter(active=True)
    for obj in qs:
        sub_perms = obj.permission.all()
        for group in obj.groups.all():
            group.permissions.set(sub_perms)