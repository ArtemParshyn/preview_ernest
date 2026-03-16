from django.urls import path
from rest_framework.routers import DefaultRouter

from api import views

urlpatterns = [
    path('component-image/', views.image),
    path('components/', views.components),
]

