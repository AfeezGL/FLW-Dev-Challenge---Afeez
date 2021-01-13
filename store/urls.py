from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name="store_home"),
    path('create/', views.CreateStore.as_view(), name="create_store"),
    path('activate/', views.ActivateStore, name="activate_store"),
    path('initialize_payment', views.InitializePayment, name="activation_payment_init"),
    path('verify_payment', views.verify_payment, name="payment_verify"),
    path('add_product', views.AddProduct.as_view(), name="add_product"),
    path('update/', views.UpdateStore.as_view(), name="update_store")
]