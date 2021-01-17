from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist


def is_rider(function):
    def wrap(request, *args, **kwargs):
        try:
            rider = request.user.dispatch_rider
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("rider_register"))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap