from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.utils.html import escape
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import TemplateResponse
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.forms import ( AdminPasswordChangeForm, UserChangeForm, UserCreationForm,)
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.urls import path, reverse
from django.db import router, transaction
from django.contrib.auth.models import Permission
from classy.models import task, completed_task, Profile, data_authorization, dataset_authorization
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class profileAdmin(admin.ModelAdmin):
    list_display = ('user_email',)
    def user_email(self, x):
        return x.user.email
    filter_horizontal = ('data_authorizations', 'dataset_authorizations',)
    fieldsets = (
        (None, {
            'fields': ('user_email',)
        }),
        ('Authorizations', {
            'fields': ('dataset_authorizations', 'data_authorizations')
        }),
    )
    readonly_fields=['user_email']

class dataAdmin(admin.ModelAdmin):
    list_display = ('name', 'datasource', 'schema', 'table', 'column')
    list_filter = ('datasource', 'schema', 'table')
    
class datasetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    filter_horizontal = ('data_authorizations',)


class taskAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'run_at', 'progress')
    list_filter = ('queue', 'priority')
    fieldsets = (
        (None, {
            'fields': ('name', 'verbose_name', 'priority', 'queue', 'error')
        }),
        ('Auto-filled fields', {
            'fields': ('run_at', 'user', 'progress')
        }),
    )
    #fields = ['name', 'priority', 'queue', 'error', 'run_at', 'finished_at']
    readonly_fields=['name', 'run_at', 'error', 'user', 'progress', 'queue']

class taskCompletedAdmin(admin.ModelAdmin):
    list_display = ('name', 'run_at', 'finished_at')

admin.site.register(Profile, profileAdmin)
admin.site.register(data_authorization, dataAdmin)
admin.site.register(dataset_authorization, datasetAdmin)
admin.site.register(task, taskAdmin)
admin.site.register(completed_task, taskCompletedAdmin)
