from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Store
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from .forms import CreateStoreForm, AddProductForm
from .mixins import HasStoreMixin
from .decorators import has_store
import json
import requests

@login_required
@has_store
def store_home(request):
    store = request.user.store
    template = "store/index.html"
    product_list = store.product_set.all()
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
@has_store
def InitializePaymentView(request):
    data = json.loads(request.body)
    res = requests.post('https://api.paystack.co/transaction/initialize', json = data, headers = {"Authorization": FLUTTERWAVE_API_KEY})
    print (res.text)
    response = res.json()
    print (response)
    return JsonResponse(response)

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