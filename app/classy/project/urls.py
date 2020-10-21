from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from classy.views import index

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path('', include('classy.urls')),
    path('admin/login/', index.index),
    path('admin/', admin.site.urls),
]

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

