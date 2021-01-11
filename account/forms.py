from .models import User
from django import forms
from django.core.exceptions import ValidationError

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label = "Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label = "Confirm Password")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number',]

    def clean_confirm_password(self):
        cd=self.cleaned_data
        if cd['confirm_password'] != cd['password']:
            raise ValidationError("passwords don't match")
               
        return cd['confirm_password']