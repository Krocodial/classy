
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.dateparse import *
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import escape
from django.forms.models import model_to_dict

from ratelimit.decorators import ratelimit

import threading, csv, json, random, os, difflib, datetime

from .models import ClassificationCount, Classification, ClassificationLogs, ClassificationReviewGroups, ClassificationReview
from .forms import *
from .scripts import calc_scheduler, upload
from .helper import query_constructor, role_checker, filter_results, custom_rate

from background_task.models import Task

from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.middleware.csrf import get_token



#Basic logout, this will end the local user session. However if the user is still authenticated with a SMSESSION cookie they will be automatically logged in again once directed to the index page. This is useful for immediately getting a new token pair from the keycloak server.
def user_logout(request):
    logout(request)
    return redirect('classy:index')


