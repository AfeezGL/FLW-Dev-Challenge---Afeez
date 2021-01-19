from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include("root.urls")),
    path('admin/', admin.site.urls),
    path('product/', include("product.urls")),
    path('checkout/', include("checkout.urls")),
    path('account/', include("account.urls")),
    path('store/', include("store.urls")),
    path('dispatch/rider/', include("dispatch.urls"))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)