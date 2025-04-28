from django.contrib import admin
from django.urls import include, path

from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from subscriptions import views as subscription_views
from checkout import views as checkout_views
from webhook import views as webhook_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls')),
    path('', home_view, name='home'),
    path('about/', about_view),
    path('protected/', pw_protected_view, name='protected'),
    path('protected/user-only/', user_only_view, name='user-only'),
    path('protected/staff-only/', staff_only_view, name='staff-only'),

    # SUBSCRIPTION URLS
    path('pricing/', subscription_views.subscription_price_view, name='pricing'),
    path('pricing/<str:interval>/', subscription_views.subscription_price_view, name='pricing_interval'),  # This is a duplicate path, consider removing it or changing the name
    path('accounts/billing/', subscription_views.user_subscription_view, name='billing_details'),
    path('accounts/billing/cancel', subscription_views.user_subscription_cancel_view, name='billing_cancellation'),

    
    # CHECKOUT URLS
    path('checkout/package/<str:price_id>/', checkout_views.product_price_redirect_view, name='product_price_redirect'),
    path('checkout/start/', checkout_views.checkout_redirect_view, name='paddle_checkout_start'),
    path('checkout/success/', checkout_views.checkout_finalize_view, name='paddle_checkout_end'),
    path('checkout/<str:checkout_subscription_price_id>/', checkout_views.checkout_start_view, name="checkout"),
    path("checkout/verfication/check", checkout_views.checkout_pending_view, name="pending_checkout"),


    #WEBHOOKS URLS
    path('webhook/transaction/complete', webhook_view.paddle_transaction_webhook_view, name="paddle_transaction_webhook"),
    path('webhook/subscription/cancelled', webhook_view.paddle_subscription_cancelled_webhook_view, name="paddle_subscription_cancelled_webhook")
]
