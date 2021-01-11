from .models import Store
from product.models import Product
from django.forms import ModelForm

class CreateStoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description", "phone_number", "bank_name", "account_number"]

class AddProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["image", "name", "description", "tags", "category", "tags"]