import account
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Store, Order
from product.models import Product
from account.models import Customer
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.generic.edit import CreateView, UpdateView
from .forms import CreateStoreForm, AddProductForm
from .mixins import HasStoreMixin
from .decorators import has_store, has_inactive_store
from datetime import datetime
import time
import requests
import json
from django.conf import settings

FLUTTERWAVE_SEC_KEY = settings.FLUTTERWAVE_SEC_KEY
BASE_URL = settings.BASE_URL



"""
    STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS
    STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS
    STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS
    STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS
    STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS      STORE ADMIN RELATED VIEWS
"""

class CreateStore(LoginRequiredMixin, CreateView):
    form_class = CreateStoreForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        store = form.save(commit=False)
        store.user = self.request.user
        store.save()
        return HttpResponseRedirect(reverse("dashboard"))


@login_required
@has_inactive_store
def ActivateStore(request):
    try:
        store = request.user.store
    except:
        return HttpResponseRedirect(reverse("create_store"))
    
    template = "store/activate.html"

    context = {
        "store": store
    }
    return render(request, template, context)


@login_required
@has_inactive_store
def InitializePayment(request):
    store = request.user.store
    timestamp = int(datetime.now().timestamp())
    redirect_url = f"{BASE_URL}{reverse('payment_verify')}"
    data = {
        "tx_ref": f"{store.name}-{timestamp}",
        "amount": "20",
        "currency": "USD",
        "redirect_url": redirect_url,
        "payment_options": "card",
        "meta": {
            "consumer_id": request.user.id,
            "consumer_email": request.user.email,
            "transaction_type": "store activation",
            "store_id": store.id
        },
        "customer":{
            "name": store.name,
            "email": store.email,
            "phone_number": str(store.phone_number)
        },
        "customizations":{
            "title":"Jumga",
            "description":"Shopping made easy",
            "logo":"https://assets.piedpiper.com/logo.png"
        }
    }
    res = requests.post('https://api.flutterwave.com/v3/payments', json = data, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
    response = res.json()
    print(response)
    link = response["data"]["link"]
    return HttpResponseRedirect(link)


def VerifyPayment(request):
    transaction_id = request.GET['transaction_id']
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    res = requests.get(url, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
    response = res.json()
    print(response)
    message = response['message']

    if res.ok:
        data = response['data']
        meta = data['meta']
        store_id = meta['store_id']
        if response['status'] == 'success' and data['charged_amount'] >= 20:
            pk = int(store_id)
            store = Store.objects.get(id=pk)
            store.is_active = True
            store.save()
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        return JsonResponse(message, safe=False)


@login_required
@has_store
def Dashboard(request):
    store = request.user.store
    template = "store/index.html"
    product_list = store.product_set.all().order_by("-date_updated")
    orders = Order.objects.filter(store=store, completed=True)
    deliveries = []
    for order in orders:
        if order.status != "DE":
            deliveries.append(order)
    length = len(deliveries)
    context = {
        "store": store,
        "product_list": product_list,
        "length": length

    }
    return render(request, template, context)


class CreateProduct(LoginRequiredMixin, HasStoreMixin, CreateView):
    form_class = AddProductForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        product = form.save(commit=False)
        product.store_id = self.request.user.store.id
        product.save()
        return HttpResponseRedirect(reverse("dashboard"))


class UpdateProduct(UpdateView):
    model = Product
    template_name = "product/forms.html"
    fields = ["image", "name", "description", "tags", "category", "price", "available_units"]

    def get_success_url(self):
        return reverse("dashboard")


def PendingOrders(request):
    store = request.user.store
    template = "store/pendingOrders.html"
    orders = Order.objects.filter(store=store, completed=True)
    pending_orders = []
    for order in orders:
        if order.status != "DE":
            pending_orders.append(order)
    context = {
        "store": store,
        "pending_orders": pending_orders
    }
    return render(request, template, context)


class OrderDetails(UpdateView):
    model = Order
    template_name = "store/orderDetails.html"
    fields = ["status"]

    def get_success_url(self):
        return reverse("order_details", kwargs={"pk": self.object.id})


class UpdateStore(LoginRequiredMixin, HasStoreMixin, UpdateView):

    def get_object(self):
        store = self.request.user.store
        return store
    
    template_name = "product/forms.html"
    fields = ["name", "description"]

    def get_success_url(self):
        return reverse("store")


def Withdraw(request):
    store = request.user.store
    timestamp = int(datetime.now().timestamp())
    if request.method == "POST":
        bank = request.POST.get("bank")
        account_number = request.POST.get("account_number")
        x = request.POST.get("amount")
        amount = int(x)
        
        if store.currency == "GHS":
            url = f"https://api.flutterwave.com/v3/banks/{bank}/branches"
            res = requests.get(url, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
            response = json.loads(res.content)
            print(response)
            branch_choices = response["data"]
            context = {
                "branch_choices": branch_choices,
                "amount": amount,
                "bank": bank,
                "account_number": account_number
            }
            template = "store/withdrawOthers.html"
            return render(request, template, context)

        data = {
            "account_bank": bank,
            "account_number": account_number,
            "amount": amount,
            "narration": "jumga store withdrawal",
            "currency": store.currency,
            "reference": f"{store.name}-withdrawal-{timestamp}",
            "callback_url": "https://hooks.zapier.com/hooks/catch/9319455/o0es6km",
            "debit_currency": store.currency
        }
        res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        if response["status"] == "success":
            store.balance -= int(amount)
            store.save()
        template = "store/withdrawalResponse.html"
        context = {
            "status": response["status"],
            "message": response["message"]
        }
        return render(request, template, context)
    else:
        if store.currency == "GBP":
            return HttpResponseRedirect(reverse("withdraw_uk"))
        else:
            url = f"https://api.flutterwave.com/v3/banks/{store.country}"
            res = requests.get(url, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
            response= json.loads(res.content)
            bank_options = list(response["data"])
            template = "store/initiateWithdrawal.html"
            context = {
                "bank_options": bank_options,
                "currency": store.currency
            }
            return render(request, template, context)
        return HttpResponseRedirect(reverse("withdraw_others", kwargs={"currenccy": store.currency}))

def branched(request):
    store = request.user.store
    timestamp = int(datetime.now().timestamp())
    branch_code = request.POST.get("branch_code")
    bank_code = request.POST.get("bank_code")
    amount = request.POST.get("amount")
    account_number = request.POST.get("account_number")
    data = {
            "account_bank": bank_code,
            "account_number": account_number,
            "amount": amount,
            "narration": "jumga store withdrawal",
            "currency": store.currency,
            "reference": f"{store.name}-withdrawal-{timestamp}",
            "callback_url": "https://hooks.zapier.com/hooks/catch/9319455/o0es6km",
            "destination_branch_code": branch_code,
            "beneficiary_name": f"{request.user.first_name} {request.user.last_name}"
        }
    res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
    response = json.loads(res.content)
    print(response)
    template = "store/withdrawalResponse.html"
    if response["status"] == "success":
        store.balance -= int(amount)
        store.save()
    context = {
        "status": response["status"],
        "message": response["message"]
    }
    return render(request, template, context)


def withdraw_uk(request):
    store = request.user.store
    timestamp = int(datetime.now().timestamp())
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        data = {
            "amount": amount,
            "narration": "jumga store withdrawal",
            "currency": "GBP",
            "reference": f"{store.name}-withdrawal-{timestamp}",
            "beneficiary_name": "John Twain",
            "meta": [
                {
                "AccountNumber": request.POST.get("account_number"),
                "RoutingNumber": request.POST.get("routing_number"), 
                "BeneficiaryName": request.POST.get("beneficiary_name"),
                "BeneficiaryCountry": "GB",
                }
            ]
        }
        res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        print(response)
        if response["status"] == "success":
            store.balance -= amount
            store.save()
        template = "store/withdrawalResponse.html"
        context = {
            "status": response["status"],
            "message": response["message"]
        }
        return render(request, template, context)

    template = "store/withdrawUk.html"
    context = {"store": store}
    return render(request, template, context)





"""
    CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS
    CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS
    CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS
    CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS
    CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS      CUSTOMER RELATED VIEWS
"""



def ProductList(request, slug):
    try:
        store = Store.objects.get(slug=slug)
    except:
        return HttpResponseNotFound("page not found")

    template = "product/index.html"
    product_list = store.product_set.all().order_by("-date_updated")
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "store": store,
        "object_list": page_obj
    }
    return render(request, template, context)


def CartView(request, slug):
    try:
        store = Store.objects.get(slug=slug)
    except:
        return HttpResponseNotFound("page not found")
    
    try:
        customer = Customer.objects.get(user = request.user)
    except:
        try:
            device_id = request.COOKIES["deviceId"]
        except:
            device_id = "empty"
        customer, created = Customer.objects.get_or_create(device_id = device_id)
    order, created = Order.objects.get_or_create(customer = customer, store = store, completed = False)
    cartitems = order.cartitem_set.all()
    template = "product/cart.html"
    return render(request, template, {"order":order,
    "cartitems":cartitems})