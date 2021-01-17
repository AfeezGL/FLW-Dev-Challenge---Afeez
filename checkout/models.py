from django.db import models
from product.models import Order
from phonenumber_field.modelfields import PhoneNumberField

class Address(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    first_name = models.CharField(max_length = 250, null = True)
    last_name = models.CharField(max_length = 250, null = True)
    email = models.EmailField(max_length = 250, null = True, blank = True)
    address_line_1 = models.CharField(max_length = 250, null = True)
    address_line_2 = models.CharField(max_length = 250, null = True, blank = True)
    city = models.CharField(max_length = 250, null = True)
    state = models.CharField(max_length = 250, null = True)
    country = models.CharField(max_length = 250, default = "Nigeria")
    postal_code = models.PositiveIntegerField(null = True)
    phone_number = PhoneNumberField()

class OrderDetails(models.Model):
    order = models.OneToOneField(Order, null=True, on_delete=models.SET_NULL)
    amount_total = models.IntegerField()
    shop_total = models.IntegerField()
    commission = models.IntegerField()
    shipping_total= models.IntegerField()
    rider_total = models.IntegerField()
    shipping_commission = models.IntegerField()