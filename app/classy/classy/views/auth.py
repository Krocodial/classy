from ratelimit.decorators import ratelimit
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import login
import os

import classy.api

from classy.views.common import helper

@ratelimit(key='header:x-forwarded-for', rate=helper.custom_rate, block=True)
def index(request):
    response = classy.api.auth.index(request)
    if response.status_code == 200:
        return redirect('classy:home')
    elif response.status_code == 302:
        return response
    else:
        return HttpResponse(500)

def login_complete(request):
    response = classy.api.auth.login_complete(request)
    print(response)
    if response.status_code == 200:
        return redirect('classy:home')
    else:
        return HttpResponse(500)
	
	
def health(request):
    return HttpResponse(200)
