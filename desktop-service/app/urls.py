from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('desktop-products/', views.desktop_product_list),
    path('desktop-products/<int:pk>/', views.desktop_product_detail),
    path('desktop-products/check/<int:pk>/', views.check_product),
    path('desktop-products/<int:pk>/import/', views.import_product),
    path('desktop-products/<int:pk>/imports/', views.import_history),
    path('desktop-products/imports/all/', views.all_imports),
]
