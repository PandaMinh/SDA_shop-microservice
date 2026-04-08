from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('carts/<int:customer_id>/', views.get_cart),
    path('carts/<int:customer_id>/clear/', views.clear_cart),
    path('cart-items/', views.add_cart_item),
    path('cart-items/<int:item_id>/', views.update_cart_item),
    path('cart-items/<int:item_id>/delete/', views.remove_cart_item),
]
