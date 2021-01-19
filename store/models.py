from django.db import models
from account.models import User, Customer
from autoslug import AutoSlugField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class CountryChoices(models.TextChoices):
	NIGERIA = 'NG', _('Nigeria')
	GHANA = 'GH', _('Ghana')
	KENYA = 'KE', _('Kenya')
	UK = 'UK', _('United Kingdom')

class CurrencyChoices(models.TextChoices):
	NIGEIRA = 'NGN', _('Nigerian naira')
	GHANA = 'GHS', _('Ghana')
	KENYA = 'KES', _('Kenya')
	UK = 'GBP', _('United Kingdom')

class Store(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	description = models.TextField()
	email = models.EmailField()
	phone_number = PhoneNumberField()
	address_line_1 = models.CharField(max_length=200, null=True)
	address_line_2 = models.CharField(max_length=200, null=True, blank=True)
	city = models.CharField(max_length=50, null=True)
	state = models.CharField(max_length=50, null=True)
	country = models.CharField(max_length=2, choices=CountryChoices.choices, default=CountryChoices.NIGERIA)
	currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.NIGEIRA)
	balance = models.IntegerField(default=0)
	is_active = models.BooleanField(default=False)
	has_rider = models.BooleanField(default=False)
	slug = AutoSlugField(populate_from='name')

	def __str__(self):
		return self.name


# The order model
class Order(models.Model):

	class StatusChoices(models.TextChoices):
		PENDING = 'PE', _('Pending')
		SORTING = 'SR', _('Sorting')
		SHIPMENT = 'SH', _('Shipping')
		DELIVERED = 'DE', _('Delivered')

	customer = models.ForeignKey(Customer, null=True, on_delete = models.SET_NULL)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	completed = models.BooleanField(default = False, null = True, blank = True)
	transaction_id = models.CharField(max_length = 200, null = True, blank = True)
	shipping_fee = models.IntegerField(default=0)
	status = models.CharField(max_length = 2, choices = StatusChoices.choices, default=StatusChoices.PENDING)
	signed = models.BooleanField(default=False)

	@property
	def reference(self):
		return self.customer.__str__() + str(self.id)
	
	@property
	def cart_total(self):
		total = 0
		for cartitem in self.cartitem_set.all():
			total += cartitem.get_price()
		return total

	def __str__(self):
		return self.customer.__str__()

