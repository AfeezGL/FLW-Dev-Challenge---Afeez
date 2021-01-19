from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import DispatchRider


def is_rider(function):
    def wrap(request, *args, **kwargs):
        try:
            rider = DispatchRider.objects.get(user=request.user)
            return function(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("rider_register"))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap