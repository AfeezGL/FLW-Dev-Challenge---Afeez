from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductList.as_view(), name="index"),
    path('product/showcase/<int:pk>/', views.ProductShowcase.as_view(), name="details"),
    path('add-to-cart/', views.add_to_cart, name = "add_to_cart"),
    path('cart', views.CartView, name = "cart" ),
    path('refresh', views.RefreshNum, name = "refresh"),
    path('reduce', views.reduce_units, name = "reduce"),
]