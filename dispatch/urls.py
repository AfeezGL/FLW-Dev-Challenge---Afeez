from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('register/', views.RegisterView.as_view(), name="register_rider"),
    path('dashboard/', views.DashboardView, name="rider_dashboard"),
    path('task/details/<int:pk>/', views.TaskDetailsView.as_view(), name="task_details"),
    path('task/update/<int:pk>/', views.TaskUpdateView.as_view(), name="task_update"),
    path('withdraw/', views.withdrawal, name="rider_withdrawal"),
    path('withdraw/uk', views.withdraw_uk, name="dispatch_withdraw_uk"),
    path('withdraw/branched/', views.branched, name="dispatch_branched_withdrawal"),
    path('admin/', views.AdminView, name="dispatch_admin"),
    path('admin/assign/store/<int:pk>', views.AssignStore, name="assign_store")
]