from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('register/', views.RegisterView.as_view, name="register_rider"),
    path('dashboard/', views.DashboardView, name="rider_dashboard"),
    path('task/details/<int:pk>', views.TaskDetailView, name="task_detail")
]