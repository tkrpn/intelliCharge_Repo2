from django.http import HttpResponse

from django.shortcuts import render, redirect
from os import path


def index(request):
    return render(request, 'demo_login.html')#, context=context)