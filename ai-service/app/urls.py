from django.urls import path

from app import views

urlpatterns = [
    path("health/", views.health_check),
    path("events/", views.track_event),
    path("chat/", views.chat),
    path("recommendations/", views.recommendations),
]
