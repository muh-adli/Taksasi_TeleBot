from django.urls import path
from .views import (
    landingPage,
    homePage,
)

urlpatterns = [
    path('', landingPage, name='landingPage'),
    path('', homePage, name='homePage'),
]