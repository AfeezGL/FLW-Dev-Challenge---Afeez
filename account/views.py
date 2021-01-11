from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from .forms import SignupForm
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from .models import User, Customer

# User registration view
class SignupView(CreateView):
	form_class = SignupForm 
	template_name = 'product/forms.html'

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated == True:
			return HttpResponseForbidden()

		return super(SignupView, self).dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		user = form.save(commit=False)
		user.set_password(form.cleaned_data['password'])
		user.save()
		Customer.objects.create(user=user)
		return HttpResponseRedirect(reverse('login'))