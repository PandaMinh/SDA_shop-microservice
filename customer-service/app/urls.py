from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('customers/register/', views.register),
    path('customers/login/', views.login),
    path('customers/<int:pk>/', views.customer_detail),

    path('orders/', views.create_order),
    path('orders/customer/', views.customer_orders),
    path('orders/all/', views.all_orders),
    path('orders/<int:order_id>/', views.order_detail),
    path('orders/<int:order_id>/status/', views.update_order_status),
    path('orders/<int:order_id>/reviews/', views.create_review),
]
