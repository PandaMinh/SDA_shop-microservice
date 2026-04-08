from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),

    # Auth
    path('api/auth/register', views.customer_register),
    path('api/auth/login', views.customer_login),
    path('api/auth/staff/login', views.staff_login),

    # Products — all
    path('api/products', views.get_all_products),
    path('api/products/mobile', views.mobile_products),
    path('api/products/desktop', views.desktop_products),
    path('api/products/clothes', views.clothes_products),
    path('api/products/mobile/<int:pk>', views.mobile_product_detail),
    path('api/products/desktop/<int:pk>', views.desktop_product_detail),
    path('api/products/clothes/<int:pk>', views.clothes_product_detail),

    # Admin product management
    path('api/admin/products/mobile', views.mobile_products),
    path('api/admin/products/mobile/<int:pk>', views.mobile_product_detail),
    path('api/admin/products/desktop', views.desktop_products),
    path('api/admin/products/desktop/<int:pk>', views.desktop_product_detail),
    path('api/admin/products/clothes', views.clothes_products),
    path('api/admin/products/clothes/<int:pk>', views.clothes_product_detail),

    # Nhập hàng (Inventory Import)
    path('api/admin/products/<str:product_type>/<int:pk>/import', views.import_product),
    path('api/admin/products/<str:product_type>/<int:pk>/imports', views.import_history),
    path('api/admin/products/imports/all', views.all_imports),

    # Cart
    path('api/cart', views.get_cart),
    path('api/cart/items', views.add_cart_item),
    path('api/cart/items/<int:item_id>', views.update_cart_item),
    path('api/cart/items/<int:item_id>/delete', views.remove_cart_item),
    path('api/cart/clear', views.clear_cart),

    # Orders
    path('api/orders/checkout', views.checkout),
    path('api/orders', views.customer_orders),
    path('api/admin/orders', views.admin_orders),
    path('api/admin/orders/<int:order_id>', views.update_order_status),

    # AI
    path('api/ai/chat', views.ai_chat),
    path('api/ai/events', views.ai_track_event),
    path('api/ai/recommendations', views.ai_recommendations),
]
