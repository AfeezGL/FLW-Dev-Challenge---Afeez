from django.db import models
from account.models import User, Customer
from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField()
    phone_number = PhoneNumberField()
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='name')

    def __str__(self):
        return self.name


# The order model
class Order(models.Model):

	class StatusChoices(models.TextChoices):
		SORTING = 'SR', _('Sorting')
		SHIPMENT = 'SH', _('Shipping')
		DELIVERED = 'DE', _('Delivered')

	customer = models.ForeignKey(Customer, null=True, on_delete = models.SET_NULL)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	completed = models.BooleanField(default = False, null = True, blank = True)
	transaction_id = models.CharField(max_length = 200, null = True, blank = True)
	status = models.CharField(max_length = 2, choices = StatusChoices.choices, default=StatusChoices.SORTING)

	@property
	def reference(self):
		return self.customer.__str__() + str(self.id)
	
	@property
	def total(self):
		total = 0
		for cartitem in self.cartitem_set.all():
			total += cartitem.get_price()
		return total

	def __str__(self):
		return self.customer.__str__()
		