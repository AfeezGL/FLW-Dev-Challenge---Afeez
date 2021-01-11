from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name="store_home"),
    path('create/', views.CreateStore.as_view(), name="create_store"),
    path('activate/', views.ActivateStore, name="activate_store"),
    path('add_product', views.AddProduct.as_view(), name="add_product"),
    path('update/', views.UpdateStore.as_view(), name="update_store")
]