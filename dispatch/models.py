import store
from django.db import models
from account.models import User
from store.models import Store

class DispatchRider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store = models.OneToOneField(Store, on_delete= models.SET_NULL, null=True)
    balance = models.IntegerField()
