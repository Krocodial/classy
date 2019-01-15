from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.decorators import login_required

admin.site.login = login_required(admin.site.login)

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('', include('classy.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
            path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

