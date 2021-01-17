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
    order = models.OneToOneField(Order, null=True, on_delete=models.SET_NULL, related_name="details")
    cart_total = models.IntegerField(default=0)
    shipping_total= models.IntegerField(default=0)

    @property
    def commission(self):
        return self.cart_total * 0.075

    @property
    def store_total(self):
        return self.cart_total - self.commission

    @property
    def shipping_commission(self):
        return self.shipping_total * 0.2
    
    @property
    def rider_total(self):
        return self.shipping_total - self.shipping_commission
    
    @property
    def net_total(self):
        return self.cart_total + self.shipping_total