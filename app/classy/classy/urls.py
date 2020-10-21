
from django.urls import path
from . import old
from classy.views import tutorial, download, review, exceptions, logs, log, modify, search, auth, home, uploader, data
import classy.api

app_name = 'classy'
urlpatterns = [
	path('api_v1/', classy.api.auth.index, name='api_index'),
    path('', auth.index, name='index'),
    path('data', data.data, name='data'),
    path('data/<int:classy_id>', log.log, name='log_detail'),
    path('uploader', uploader.uploader, name='uploader'),
    path('search', search.search, name='search'),
    path('home', home.home, name='home'),
    path('modifiy', modify.modify, name='modi'),
    path('review', review.review, name='review'),
    path('exceptions', exceptions.exceptions, name='exceptions'),
    path('logs', logs.logs, name='log_list'),
    path('download', download.download, name='download'),
    path('tutorial', tutorial.tutorial, name='tutorial'),
    path('health', auth.health, name='health'),
    path('login', auth.login_complete, name='login'),
]

