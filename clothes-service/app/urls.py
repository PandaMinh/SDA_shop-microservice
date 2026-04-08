from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('clothes-products/', views.product_list),
    path('clothes-products/<int:pk>/', views.product_detail),
    path('clothes-products/check/<int:pk>/', views.product_check),
    path('clothes-products/<int:pk>/import/', views.import_product),
    path('clothes-products/<int:pk>/imports/', views.import_history),
    path('clothes-products/imports/all/', views.all_imports),
]
