from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('staff/login/', views.staff_login),
    path('staff/verify/', views.verify_token),
    path('staff/<int:pk>/', views.staff_detail),
]
