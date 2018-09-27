from django.contrib import admin
from django.contrib.auth.models import Permission
# Register your models here.

<<<<<<< HEAD
from .models import classification

admin.site.register(Permission)
#admin.site.register(classification)
=======
from .models import permissions
>>>>>>> 4ae3ddc16cb17e3c7c8091a5a9cfb757c6935700

admin.site.register(permissions)
admin.site.register(Permission)
