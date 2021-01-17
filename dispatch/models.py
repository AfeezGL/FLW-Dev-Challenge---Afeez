from django.db.models.fields import CharField
import store
from django.db import models
from account.models import User
from phonenumber_field.modelfields import PhoneNumberField

class DispatchRider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="dispatch_rider")
    phone_number = PhoneNumberField()
    bank = CharField(max_length=50)
    account_number = models.IntegerField()
    balance = models.IntegerField(blank=True, default=0)
