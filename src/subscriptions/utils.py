import helpers.billing

from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription

def refresh_users_subs(user_ids=None, active_only=True, days_ago=0, days_left=0, day_start=0, day_end=0, verbose=False):
    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    if days_ago > 0:
        qs = qs.by_days_ago(days_ago=days_ago)
    if days_left > 0:
        qs = qs.by_days_left(days_left=days_left)
    if day_start > 0 and day_end > 0:
        qs = qs.by_range(day_start=day_start, day_end=day_end)

    complete_count = 0
    qs_count = qs.count()

    for obj in qs:
        if verbose:
            print("Updating user", obj.user, obj.subscription, obj.ends_at)
        if obj.paddle_id:
            sub_data = helpers.billing.get_subscription_plan(obj.paddle_id, raw=False)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            obj.save()
            complete_count += 1
    return complete_count == qs_count



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