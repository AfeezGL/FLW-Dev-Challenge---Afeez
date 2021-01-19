from django.db import models
from account.models import User
from phonenumber_field.modelfields import PhoneNumberField
from store.models import Store, CountryChoices

class DispatchRider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    country = models.CharField(max_length=2, choices=CountryChoices.choices, default=CountryChoices.NIGERIA)
    store = models.OneToOneField(Store, null=True, on_delete=models.SET_NULL, related_name="rider")
    has_store = models.BooleanField(default=False)
    balance = models.IntegerField(blank=True, default=0)