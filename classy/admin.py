from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from background_task.models_completed import CompletedTask
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from classy.models import Profile, DataAuthorization, DatasetAuthorization, Application
from background_task.admin import TaskAdmin, CompletedTaskAdmin
from background_task.models_completed import CompletedTask
from background_task.models import Task
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    filter_horizontal = ('data_authorizations', 'dataset_authorizations',)

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', )
        }),
        
    )

    readonly_fields=['email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

class CustomTaskAdmin(TaskAdmin):
    readonly_fields=['task_name', 'task_params', 'task_hash', 'verbose_name', 'repeat', 'repeat_until', 'queue', 'attempts', 'failed_at', 'last_error', 'locked_by', 'locked_at', 'creator_content_type', 'creator_object_id']

class CustomCompletedTaskAdmin(CompletedTaskAdmin):
    readonly_fields=['task_name', 'task_params', 'task_hash', 'verbose_name', 'repeat', 'repeat_until', 'queue', 'attempts', 'failed_at', 'last_error', 'locked_by', 'locked_at', 'creator_content_type', 'creator_object_id', 'priority', 'run_at']

class ProfileAdmin(admin.ModelAdmin):
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

class DataAdmin(admin.ModelAdmin):
    list_display = ('name', 'datasource', 'schema', 'table', 'column')
    list_filter = ('datasource', 'schema', 'table')
    
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    filter_horizontal = ('data_authorizations',)

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym')
    list_filter = ('poc',)
    ordering = ('name',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Task)
admin.site.register(Task, CustomTaskAdmin)

admin.site.unregister(CompletedTask)
admin.site.register(CompletedTask, CustomCompletedTaskAdmin)

admin.site.unregister(Group)
admin.site.register(Application, ApplicationAdmin)
#admin.site.register(Profile, ProfileAdmin)
admin.site.register(DataAuthorization, DataAdmin)
admin.site.register(DatasetAuthorization, DatasetAdmin)
