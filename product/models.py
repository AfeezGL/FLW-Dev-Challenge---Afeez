from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from store.models import Store, Order
from account.models import User, Customer

# Create your models here.

class Category(models.Model):
	name = models.CharField(max_length=150)

	def __str__(self):
		return self.name

class Tag(models.Model):
	name = models.CharField(max_length=50)
	
	def __str__(self):
		return self.name
		
		

class Product(models.Model):
	name = models.CharField(max_length=150)
	image = models.ImageField(null = True)
	description = models.TextField(null=True, blank=True)
	price = models.PositiveIntegerField()
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
	tags = models.ManyToManyField(Tag, blank=True)
	available_units = models.PositiveIntegerField(blank=False, default=1)
	date_created = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)
	
	@property
	def commission(self):
		commission = self.price * 0.075
		if commission < 10000:
			return commission
		return 10000
	
	def __str__(self):
		return self.name


#cart item model
class CartItem(models.Model):
	product = models.ForeignKey(Product, null=True, on_delete = models.SET_NULL)
	units = models.PositiveIntegerField(default = 0, blank = True)
	customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
	order = models.ForeignKey(Order, null = True, on_delete = models.SET_NULL)
	date_added = models.DateTimeField(auto_now_add=True)

	def max_unit(self):
		return self.product.available_units
	
	def get_price(self):
		return int((self.product.price * self.units))

	def __str__(self):
		return self.product.name
