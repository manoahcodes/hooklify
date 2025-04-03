from django.contrib import admin
from .models import Customer

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ('paddle_id', 'init_email', 'user')
    list_display = ["user", "paddle_id"]

admin.site.register(Customer, CustomerAdmin)