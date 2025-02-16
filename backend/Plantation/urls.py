from django.urls import path

from .views import taksasiPage


urlpatterns = [
    path('taksasi/', taksasiPage, name='taksasiPage'),
]