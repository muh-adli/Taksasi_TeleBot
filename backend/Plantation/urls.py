from django.urls import path

from .views import taksasiPage, perawatanHome


urlpatterns = [
    path('taksasi/', taksasiPage, name='taksasiPage'),
    path('perawatan/', perawatanHome, name='perawatanHome'),
]