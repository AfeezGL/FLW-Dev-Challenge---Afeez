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
from jumga.withdrawals import Withdraw
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
        return reverse("pending_orders")


class UpdateStore(LoginRequiredMixin, HasStoreMixin, UpdateView):

    def get_object(self):
        store = self.request.user.store
        return store
    
    template_name = "product/forms.html"
    fields = ["name", "description"]

    def get_success_url(self):
        return reverse("store")


@login_required
@has_store
def withdrawal(request):
    model = request.user.store
    currency = model.currency
    app = "store"
    timestamp = int(datetime.now().timestamp())
    reference = f"store-{model.name}-withdrawal-{timestamp}"
    withdrawal_request = Withdraw(request, model, app, currency)
    # WHEN WITHDRAWAL FORM GETS SUBMITTED
    if request.method == "POST":
        bank = request.POST.get("bank")
        account_number = request.POST.get("account_number")
        x = request.POST.get("amount")
        amount = int(x)
        withdrawal_request = Withdraw(request, model, app, currency, bank=bank, account_number=account_number, amount=amount, reference=reference)
        # IF BENEFICIARY'S CURRENCY IS GHS
        if currency == "GHS":
            return withdrawal_request.get_branches(run=True)
        
        # IF THE CURRENCY IS NGN OR KES, PROCEED WITH WITHDRAWAL REQUEST
        return withdrawal_request.ngn_or_kes(run=True)
    
    # ON THEIR FIRST ATTEMPT OF WITHDRAWAL
    # IF THE CURRENCY IS POUNDS, REDIRECT THEM TO THE UK WITHDRAWAL VIEW
    if currency == "GBP":
        return HttpResponseRedirect(reverse("withdraw_uk"))
    
    # IF IT ISN'T, SEND THEM WITHDRAWAL FORM
    return withdrawal_request.send_withdrawal_form(run=True)




# THIS IS WHERE THE GHANAIAN WITHDRAWAL FORM IS FINALLY PROCESSED
@login_required
@has_store
def branched(request):
    model = request.user.store
    currency = model.currency
    app = "store"
    timestamp = int(datetime.now().timestamp())
    reference = f"store-{model.name}-withdrawal-{timestamp}"
    branch_code = request.POST.get("branch_code")
    bank_code = request.POST.get("bank_code")
    amount = int(request.POST.get("amount"))
    account_number = request.POST.get("account_number")
    beneficiary_name = f"{request.user.first_name} {request.user.last_name}"

    withdrawal_request = Withdraw(request, model, app, currency, account_number=account_number, amount=amount, reference=reference, bank_code=bank_code, branch_code=branch_code, beneficiary_name=beneficiary_name)
    return withdrawal_request.withdraw_ghs(run=True)


@login_required
@has_store
def withdraw_uk(request):
    user = request.user
    model = user.store
    currency = model.currency
    app = "store"
    timestamp = int(datetime.now().timestamp())
    reference = f"store-{model.name}-withdrawal-{timestamp}"

    
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        account_number = request.POST.get("account_number")
        routing_number = request.POST.get("routing_number")
        currency = "GBP"
        beneficiary_name = request.POST.get("beneficiary_name")

        withdrawal_request = Withdraw(request, model, app, currency, account_number=account_number, amount=amount, reference=reference,  beneficiary_name=beneficiary_name, routing_number=routing_number)
        
        return withdrawal_request.withdraw_uk(run=True)

    template = "store/withdrawUk.html"
    context = {"store": model}
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