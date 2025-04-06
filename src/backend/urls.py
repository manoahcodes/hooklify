from django.contrib import admin
from django.urls import include, path

from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from subscriptions import views as subscription_views
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls')),
    path('', home_view, name='home'),
    path('about/', about_view),
    path('protected/', pw_protected_view, name='protected'),
    path('protected/user-only/', user_only_view, name='user-only'),
    path('protected/staff-only/', staff_only_view, name='staff-only'),
    path('pricing/', subscription_views.subscription_price_view, name='pricing'),
    path('pricing/<str:interval>/', subscription_views.subscription_price_view, name='pricing_interval'),  # This is a duplicate path, consider removing it or changing the name

]
