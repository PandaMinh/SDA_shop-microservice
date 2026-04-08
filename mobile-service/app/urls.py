from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('mobile-products/', views.mobile_product_list),
    path('mobile-products/<int:pk>/', views.mobile_product_detail),
    path('mobile-products/check/<int:pk>/', views.check_product),
    path('mobile-products/<int:pk>/import/', views.import_product),
    path('mobile-products/<int:pk>/imports/', views.import_history),
    path('mobile-products/imports/all/', views.all_imports),
]
