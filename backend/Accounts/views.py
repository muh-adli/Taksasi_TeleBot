# import logging

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now


## Create your views here.
def landingPage(request):
    return render(request, "Accounts/page_landing.html", {})

def homePage(request):
    return render(request, "Accounts/page_home.html", {})


## Error Pages
def page400 (request, exception):
    return render(request, 'Error/page_404.html', status=400)
def page403 (request, exception):
    return render(request, 'Error/page_404.html', status=403)
def page404 (request, exception):
    return render(request, 'Error/page_404.html', status=404)
def page500(request):
    return render(request, 'Error/page_404.html', status=500)