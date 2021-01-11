from django.db import models
from account.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=35, default='Jumga Default')
    description = models.TextField()
    phone_number = PhoneNumberField()
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name