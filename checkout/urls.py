from django.urls import path
from . import views

urlpatterns = [
    path('<str:slug>/', views.CheckoutView, name = "checkout" ),
    path('<str:slug>/delivery-info/', views.DeliveryInfo.as_view(), name = "delivery_info"),
    path('<str:slug>/initialize/payment/', views.InitializePaymentView, name = "payment_init"),
    path('verify/payment/', views.VerifyPaymentView, name = "verify")
]