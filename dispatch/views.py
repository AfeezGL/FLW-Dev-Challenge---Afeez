from checkout.models import OrderDetails
from django.contrib.auth import models
from dispatch.decorators import is_rider
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from .models import DispatchRider
from store.models import Order, Store
from .forms import RiderForm


class IndexView(TemplateView):
    template_name = "dispatch/index.html"



def AdminView(request):
    """
        Returns a list of riders that has not been assigned a store.
    """
    riders = DispatchRider.objects.filter(has_store = False)
    template = "dispatch/admin.html"
    context = {"riders": riders}
    return render(request, template, context)


def AssignStore(request, pk):
    """
        View for assigning a Rider to a store without a rider in the same country
    """
    rider = DispatchRider.objects.get(id=pk)

    if request.method == "POST":
        store_id = request.POST.get("store_id")
        store = Store.objects.get(id=store_id)
        rider.store = store
        rider.has_store = True
        rider.save()
        store.has_rider = True
        store.save()
        return HttpResponseRedirect(reverse("dispatch_admin"))

    stores = Store.objects.filter(is_active=True, has_rider=False, country=rider.country)
    template = "dispatch/assignStore.html"
    context = {
        "stores": stores,
        "rider": rider
    }
    return render(request, template, context)





class RegisterView(LoginRequiredMixin, CreateView):
    """
        Registration View for riders
        Returns Registation form and redirects riders to their dashboard After Registration
    """
    model = DispatchRider
    form_class = RiderForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        rider = form.save(commit=False)
        rider.user_id = self.request.user.id
        rider.save()
        return HttpResponseRedirect(reverse("rider_dashboard"))



@login_required
@is_rider
def DashboardView(request):
    """
        Dispatch rider dashboard view.
        Returns a list of active orders assigned to the rider
    """
    rider = DispatchRider.objects.get(user=request.user)
    store = rider.store
    template = "dispatch/dashboard.html"
    deliveries = Order.objects.filter(completed=True, store=store, signed=False)
    length = len(deliveries)
    context = {"deliveries": deliveries, "length": length, "rider": rider}
    return render(request, template, context)


class TaskDetailsView(DetailView):
    """
        Task Detail View, Return Details of the Order to the rider
    """
    model = Order
    template_name = "dispatch/taskDetails.html"


class TaskUpdateView(UpdateView):
    """
        Allows Rider to update the Status of an Order Object through the delivery process
    """
    model = Order
    fields = ["status"]
    template_name = "dispatch/taskUpdate.html"

    def form_valid(self, form):
        form.save()
        id = self.kwargs['pk']
        order = Order.objects.get(id=id)
        if order.status == "DE" and order.signed == False:
            order.signed = True
            rider = order.store.rider
            rider.balance += order.details.rider_total
            rider.save()
            order.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse('task_details', kwargs={'pk': self.object.id})

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