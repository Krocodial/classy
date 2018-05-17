from django.contrib import admin
from django.contrib.auth.models import Permission
# Register your models here.

from .models import classification

admin.site.register(Permission)
#admin.site.register(classification)

