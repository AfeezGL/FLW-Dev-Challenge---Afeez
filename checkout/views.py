from django.shortcuts import render, reverse
from product.models import *
from account.models import Customer
from .models import Address, OrderDetails
from store.models import Store
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.generic import UpdateView
import requests
import json
import datetime
import random
from django.conf import settings

FLUTTERWAVE_SEC_KEY = settings.FLUTTERWAVE_SEC_KEY
BASE_URL = settings.BASE_URL

class DeliveryInfo(UpdateView):
    template_name = "product/forms.html"

    def get_object(self):
        user = self.request.user
        deviceId = self.request.COOKIES["deviceId"]
        slug = self.kwargs["slug"]
        try:
            store = Store.objects.get(slug = slug)
        except:
            return HttpResponseNotFound("page not found")

        try:
            customer = Customer.objects.get(user = user)
        except:
            customer, created = Customer.objects.get_or_create(device_id = deviceId)
        order, created = Order.objects.get_or_create(customer = customer, store = store, completed = False)
        address, created = Address.objects.get_or_create(order = order)
        return address
    
    fields = ['first_name', 'last_name', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'postal_code', 'phone_number']

    def get_success_url(self):
        slug = self.kwargs["slug"]
        return reverse('checkout', kwargs = {"slug": slug})


def CheckoutView(request, slug):
    template = "product/checkout.html"

    try:
        store = Store.objects.get(slug = slug)
    except:
        return HttpResponseNotFound("page not found")

    try:
        customer= Customer.objects.get(user = request.user)
    except:
        deviceId = request.COOKIES["deviceId"]
        customer, created = Customer.objects.get_or_create(device_id = deviceId)
    order, created = Order.objects.get_or_create(customer = customer, store = store, completed = False)

    # Generate transaction id
    string = str(datetime.datetime.now().timestamp())
    order.transaction_id = string

    # Generate shipping fee
    number = random.randint(800, 1200)
    order.shipping_fee = number
    order.save()

    # Generate Order Details
    details, created = OrderDetails.objects.get_or_create(order = order)
    details.cart_total = int(order.cart_total)
    details.shipping_total = int(order.shipping_fee)
    details.save()

    # Get cart items
    cartitems = order.cartitem_set.all()
    return render(request, template, {"order":order,
    "cartitems":cartitems})


def InitializePaymentView(request, slug):
    try:
        store = Store.objects.get(slug = slug)
    except:
        return HttpResponseNotFound("page not found")

    try:
        customer= Customer.objects.get(user = request.user)
    except:
        deviceId = request.COOKIES["deviceId"]
        customer, created = Customer.objects.get_or_create(device_id = deviceId)
    order, created = Order.objects.get_or_create(customer = customer, store = store, completed = False)

    try:
        email = request.user.email
        phone_number = str(request.user.phone_number)
        name = f"{request.user.first_name} {request.user.last_name}"
    except:
        email = order.address.email
        phone_number = str(order.address.phone_number)
        name = f"{order.address.first_name} {order.address.last_name}"
    
    redirect_url = f"{BASE_URL}{reverse('verify')}"

    data = {
        "tx_ref": f"{order.transaction_id}",
        "amount": f"{order.details.net_total}",
        "currency": order.store.currency,
        "redirect_url": redirect_url,
        "payment_options": "card",
        "meta": {
            "consumer_id": customer.id,
            "consumer_email": email,
            "transaction_type": "cart checkout",
        },
        "customer":{
            "name": name,
            "email": email,
            "phone_number": phone_number
        },
        "customizations":{
            "title":"Jumga",
            "description":"Shopping made easy",
            "logo":"https://assets.piedpiper.com/logo.png"
        }
    }
    res = requests.post('https://api.flutterwave.com/v3/payments', json = data, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
    response = res.json()
    link = response["data"]["link"]
    return HttpResponseRedirect(link)


def VerifyPaymentView(request):
    try:
        tx_ref = request.GET['tx_ref']
    except:
        tx_ref = None
    
    try:
        fl_tx_ref = request.GET['transaction_id']
    except:
        fl_tx_ref = None
    
    try:
        status = request.GET['status']
    except:
        status = None
    if status == "successful":
        order = Order.objects.get(transaction_id = tx_ref)
        url = f"https://api.flutterwave.com/v3/transactions/{fl_tx_ref}/verify"
        res = requests.get(url, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        content = json.loads(res.content)
        message = content["status"]

        if res.ok and message == "success":
            if order.completed:
                pass
            else:
                order.completed = True
                order.save()
                store = order.store
                store.balance += order.details.store_total
                store.save()
        else:
            message = "status"
        return HttpResponse(message)
    return HttpResponse(status)