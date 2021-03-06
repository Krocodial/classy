
from django.urls import path
from . import views

app_name = 'classy'
urlpatterns = [
    path('', views.index, name='index'),
    path('data', views.data, name='data'),
    path('data/<int:classy_id>', views.log_detail, name='log_detail'),
    #path('user_logout', views.user_logout, name='user_logout'),
    path('uploader', views.uploader, name='uploader'),
    path('search', views.search, name='search'),
    path('home', views.home, name='home'),
    #path('test', views.test, name='test'),
    path('modi', views.modi, name='modi'),
    #path('review', views.review, name='review'),
    path('exceptions', views.exceptions, name='exceptions'),
    path('log_list', views.log_list, name='log_list'),
    path('download', views.download, name='download'),
    path('tutorial', views.tutorial, name='tutorial'),
    path('health', views.health, name='health'),
    #path('gov_temp', views.gov_temp, name='gov_temp'),
    path('login_complete', views.login_complete, name='login_complete'),
]

