from django.urls import path
from . import views

urlpatterns = [
    path('<slug>/products/', views.ProductList, name="product_list"),
    path('<slug>/cart/', views.CartView, name = "cart" ),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('create/', views.CreateStore.as_view(), name="create_store"),
    path('activate/', views.ActivateStore, name="activate_store"),
    path('orders/pending/', views.PendingOrders, name="pending_orders"),
    path('orders/details/<int:pk>/', views.OrderDetails.as_view(), name="order_details"),
    path('initialize_payment', views.InitializePayment, name="activation_payment_init"),
    path('verify_payment', views.VerifyPayment, name="payment_verify"),
    path('add_product', views.CreateProduct.as_view(), name="add_product"),
    path('update/', views.UpdateStore.as_view(), name="update_store")
]