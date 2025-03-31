from django.contrib import admin
from django.urls import include, path

from .views import home_view, about_view, pw_protected_view, user_only_view, staff_only_view
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls')),
    path('', home_view, name='home'),
    path('about/', about_view),
    path('login/', account_views.login_view, name='login'),
    path('signup/', account_views.register_view, name='register'),
    path('protected/', pw_protected_view, name='protected'),
    path('protected/user-only/', user_only_view, name='user-only'),
    path('protected/staff-only/', staff_only_view, name='staff-only'),
]
