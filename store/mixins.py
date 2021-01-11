from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist


class HasStoreMixin:

    def dispatch(self, request, *args, **kwargs):
        try:
            store = request.user.store
            if store.is_active:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseRedirect(reverse("activate_store"))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse("create_store"))