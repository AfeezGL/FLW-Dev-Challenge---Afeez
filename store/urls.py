from django.urls import path
from . import views

urlpatterns = [
    path('<slug>/', views.ProductList, name="product_list"),
    path('<slug>/cart/', views.CartView, name = "cart" ),
    path('', views.Dashboard, name="dashboard"),
    path('create/your/store/', views.CreateStore.as_view(), name="create_store"),
    path('activate/yout/store/', views.ActivateStore, name="activate_store"),
    path('orders/pending/', views.PendingOrders, name="pending_orders"),
    path('orders/details/<int:pk>/', views.OrderDetails.as_view(), name="order_details"),
    path('initialize_payment', views.InitializePayment, name="activation_payment_init"),
    path('verify_payment', views.VerifyPayment, name="payment_verify"),
    path('create/product/', views.CreateProduct.as_view(), name="create_product"),
    path('update/product/<int:pk>/', views.UpdateProduct.as_view(), name="update_product"),
    path('dashboard/withdraw/', views.withdrawal, name="withdraw"),
    path('dashboard/withdraw/branched/', views.branched, name="branched"),
    path('dashboard/withdraw/uk/', views.withdraw_uk, name="withdraw_uk"),
    path('update/', views.UpdateStore.as_view(), name="update_store")
]