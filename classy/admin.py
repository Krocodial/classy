from django.contrib import admin
from django.contrib.auth.models import Permission
from classy.models import task, completed_task
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Permission)

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


admin.site.register(task, taskAdmin)
admin.site.register(completed_task, taskCompletedAdmin)
