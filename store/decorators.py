from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist


def has_store(function):
    def wrap(request, *args, **kwargs):
        try:
            store = request.user.store
            if store.is_active:
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse("activate_store"))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("create_store"))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def has_inactive_store(function):
    def wrap(request, *args, **kwargs):
        try:
            store = request.user.store
            if not store.is_active:
                return function(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse("dashboard"))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("create_store"))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap