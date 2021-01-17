from django.contrib.auth import models
from dispatch.decorators import is_rider
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from .models import DispatchRider
from store.models import Order
from .forms import RiderForm


class IndexView(TemplateView):
    template_name = "dispatch/index.html"

class RegisterView(LoginRequiredMixin, CreateView):
    model = DispatchRider
    form_class = RiderForm
    template_name = "product/forms.html"

    def form_valid(self, form):
        rider = form.save(commit=False)
        rider.user_id = self.request.user.id
        rider.save()
        return HttpResponseRedirect(reverse("rider_dashboard"))

def AdminView(request):
    orders = Order.objects.filter(completed=True)
    template = "dispatch/admin.html"
    tasks = []
    for order in orders:
        if order.status != "DE":
            tasks.append(order)
    context = {"tasks": tasks}
    return render(request, template, context)

@login_required
@is_rider
def DashboardView(request):
    rider = request.user.dispatch_rider
    template = "dispatch/dashboard.html"
    orders = Order.objects.filter(completed=True, dispatch_rider=rider)
    deliveries = []
    for order in orders:
        if order.status != "DE":
            deliveries.append(order)
    print(deliveries)
    length = len(deliveries)
    context = {"deliveries": deliveries, "length": length}
    return render(request, template, context)

class AssignTask(UpdateView):
    model = Order
    fields = ["status", "dispatch_rider"]
    template_name = "dispatch/assignTask.html"

    def get_success_url(self):
        return reverse('dispatch_admin')

class TaskDetailsView(DetailView):
    model = Order
    template_name = "dispatch/taskDetails.html"

class TaskUpdateView(UpdateView):
    model = Order
    fields = ["status"]
    template_name = "dispatch/taskUpdate.html"

    def get_success_url(self):
        return reverse('task_details', kwargs={'pk': self.object.id})