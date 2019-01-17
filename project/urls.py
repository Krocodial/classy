from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from classy import views

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path('', include('classy.urls')),
    path('admin/login/', views.index),
    path('admin/', admin.site.urls),
]

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

