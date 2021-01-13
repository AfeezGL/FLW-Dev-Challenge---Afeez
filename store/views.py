from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Store
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from .forms import CreateStoreForm, AddProductForm
from .mixins import HasStoreMixin
from .decorators import has_store, has_inactive_store
from datetime import datetime
import json
import requests
from django.conf import settings

FLUTTERWAVE_SEC_KEY = settings.FLUTTERWAVE_SEC_KEY
BASE_URL = "http://127.0.0.1:8000"

@login_required
@has_store
def store_home(request):
    store = request.user.store
    template = "store/index.html"
    product_list = store.product_set.all().order_by("-date_updated")
    context = {
        "store": store,
        "product_list": product_list
    }
    return render(request, template, context)
  
class CreateStore(LoginRequiredMixin, CreateView):
    form_class = CreateStoreForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        store = form.save(commit=False)
        store.user = self.request.user
        store.save()
        return HttpResponseRedirect(reverse("store_home"))

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
    timestamp = str(datetime.now().timestamp())
    redirect_url = f"{BASE_URL}{reverse('payment_verify')}"
    data = {
        "tx_ref": f"{store.name}-{timestamp}",
        "amount": "5000",
        "currency": "NGN",
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
    link = response["data"]["link"]
    return HttpResponseRedirect(link)


def verify_payment(request):
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
        if response['status'] == 'success' and data['charged_amount'] >= 5000:
            pk = int(store_id)
            store = Store.objects.get(id=pk)
            store.is_active = True
            store.save()
            return HttpResponseRedirect(reverse('store_home'))
    else:
        return JsonResponse(message, safe=False)


class UpdateStore(LoginRequiredMixin, HasStoreMixin, UpdateView):

    def get_object(self):
        store = self.request.user.store
        return store
    
    template_name = "product/forms.html"
    fields = ["name", "description"]

    def get_success_url(self):
        return reverse("store")

class AddProduct(LoginRequiredMixin, HasStoreMixin, CreateView):
    form_class = AddProductForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        product = form.save(commit=False)
        product.store_id = self.request.user.store.id
        product.save()
        return HttpResponseRedirect(reverse("add_product"))