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
from jumga.withdrawals import Withdraw
from datetime import datetime


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

def withdrawal(request):
    user = request.user
    model = request.user.dispatchrider
    currency = model.store.currency
    app = "dispatch"
    timestamp = int(datetime.now().timestamp())
    reference = f"rider-{user.first_name}-{user.last_name}-withdrawal-{timestamp}"
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
        return HttpResponseRedirect(reverse("dispatch_withdraw_uk"))
    
    # IF IT ISN'T, SEND THEM WITHDRAWAL FORM
    return withdrawal_request.send_withdrawal_form(run=True)

# THIS IS WHERE THE GHANAIAN WITHDRAWAL FORM IS FINALLY PROCESSED
def branched(request):
    user = request.user
    model = request.user.dispatchrider
    currency = model.store.currency
    app = "dispatch"
    timestamp = int(datetime.now().timestamp())
    reference = f"rider-{user.first_name}-{user.last_name}-withdrawal-{timestamp}"
    branch_code = request.POST.get("branch_code")
    bank_code = request.POST.get("bank_code")
    amount = request.POST.get("amount")
    account_number = request.POST.get("account_number")
    beneficiary_name = f"{request.user.first_name} {request.user.last_name}"

    withdrawal_request = Withdraw(request, model, app, currency, account_number=account_number, amount=amount, reference=reference, bank_code=bank_code, branch_code=branch_code, beneficiary_name=beneficiary_name)
    return withdrawal_request.withdraw_ghs(run=True)



def withdraw_uk(request):
    user = request.user
    model = user.dispatchrider
    currency = model.store.currency
    app = "dispatch"
    timestamp = int(datetime.now().timestamp())
    reference = f"rider-{user.first_name}-{user.last_name}-withdrawal-{timestamp}"

    
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        account_number = request.POST.get("account_number")
        routing_number = request.POST.get("routing_number")
        currency = "GBP"
        beneficiary_name = request.POST.get("beneficiary_name")

        withdrawal_request = Withdraw(request, model, app, currency, account_number=account_number, amount=amount, reference=reference,  beneficiary_name=beneficiary_name, routing_number=routing_number)
        
        return withdrawal_request.withdraw_uk(run=True)

    template = "dispatch/withdrawUk.html"
    context = {"store": user}
    return render(request, template, context)