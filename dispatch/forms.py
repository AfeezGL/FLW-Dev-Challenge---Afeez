from .models import DispatchRider
from django.forms import ModelForm

class RiderForm(ModelForm):
    class Meta:
        model = DispatchRider
        fields = ["phone_number", "bank", "account_number"]