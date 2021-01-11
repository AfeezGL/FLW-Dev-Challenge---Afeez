from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product, CartItem, Order
from account.models import User, Customer
from django.http import HttpResponse, JsonResponse
import json


class ProductList(ListView):
    model = Product
    queryset = Product.objects.all().order_by("-date_updated")
    paginate_by = 9
    template_name = "product/index.html"

class ProductShowcase(DetailView):
    model = Product
    template_name = "product/details.html"

# Add to cart view
def add_to_cart(request):
	data = json.loads(request.body)
	product_id = data["productId"]
	device_id = data["deviceId"]
	product = Product.objects.get(id = product_id)
	if request.user.is_authenticated:
		customer = Customer.objects.get(user = request.user)
	else:
		customer, created = Customer.objects.get_or_create(device_id = device_id)
	order, created = Order.objects.get_or_create(customer = customer, completed = False)
	cartitem, created = CartItem.objects.get_or_create(product = product, customer = customer, order = order)
	cartitem.units = (cartitem.units + 1)
	cartitem.save()
	units = cartitem.units
	total = order.total
	res = {
		"total":total,
		"units":units
	}
	#print (res)
	return JsonResponse(res, safe=False)

#Cart View. Shows all cart items and total
def CartView(request):
    template = "product/cart.html"
    try:
        customer = Customer.objects.get(user = request.user)
    except:
        try:
            device_id = request.COOKIES["deviceId"]
        except:
            device_id = "empty"
        customer, created = Customer.objects.get_or_create(device_id = device_id)
    order, created = Order.objects.get_or_create(customer = customer, completed = False)
    cartitems = order.cartitem_set.all()
    return render(request, template, {"order":order,
    "cartitems":cartitems})

def RefreshNum(request):
	data = json.loads(request.body)
	device_id = data["deviceId"]
	try:
		customer = Customer.objects.get(user = request.user)
	except:
		customer, created = Customer.objects.get_or_create(device_id = device_id)
	order, created = Order.objects.get_or_create(customer = customer, completed = False)
	print(order)
	cartitems = order.cartitem_set.all()
	num = 0
	for cartitem in cartitems:
		num += cartitem.units
	return JsonResponse(num, safe=False)

# Reduce cartitem units
def reduce_units(request):
	data = json.loads(request.body)
	product_id = data["productId"]
	device_id = data["deviceId"]
	product = Product.objects.get(id = product_id)
	try:
		customer = Customer.objects.get(user = request.user)
	except:
		customer, created = Customer.objects.get_or_create(device_id = device_id)
	order, created = Order.objects.get_or_create(customer = customer, completed = False)
	cartitem, created = CartItem.objects.get_or_create(product = product, customer = customer, order = order)
	cartitem.units = (cartitem.units - 1)
	if cartitem.units >= 1:
		cartitem.save()
		units = cartitem.units
	else:
		cartitem.delete()
		units = 0
	total = order.total
	res = {
		"total":total,
		"units":units
	}
	return JsonResponse(res, safe=False)