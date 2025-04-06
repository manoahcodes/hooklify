import helpers.billing
from django.conf import settings
from django.db import models

from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_email_confirmed
)

User = settings.AUTH_USER_MODEL

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    paddle_id = models.CharField(max_length=255, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True)
    init_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.paddle_id:
            if self.init_email_confirmed and self.init_email:
                email = self.init_email
                name = self.user.username
                if email != "" or email is not None and email:
                    # Check if the customer already exists in Paddle
                        customers = helpers.billing.paddle.customers.list()
                        customers_list = list(customers)
                        matching_customer = next(
                            (customer for customer in customers_list if customer.email == email),
                            None
                        )
                if matching_customer:
                    self.paddle_id = matching_customer.id
                    helpers.billing.paddle.customers.update(
                        customer_id=self.paddle_id, operation=helpers.billing.UpdateCustomer(
                            email=email,
                            name=name,
                            custom_data={
                                "user_id": self.user.id, 
                                "username": self.user.username
                                },
                        )
                )
                else:
                    new_customer = helpers.billing.create_customers(
                            raw=False, 
                            name=name, 
                            email=email, 
                            custom_data={
                                "user_id": self.user.id, 
                                "username": self.user.username
                                },
                        )
                    self.paddle_id = new_customer
        super().save(*args, **kwargs)

def allauth_user_signed_up_handler(request, user, *args, **kwargs):
    email = user.email
    Customer.objects.create(
        user=user,
        init_email=email,
        init_email_confirmed=False
    )

allauth_user_signed_up.connect(allauth_user_signed_up_handler)

def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    qs = Customer.objects.filter(
        init_email=email_address,
        init_email_confirmed=False
    )
    for obj in qs:
        obj.init_email_confirmed=True
        obj.save()

allauth_email_confirmed.connect(allauth_email_confirmed_handler)