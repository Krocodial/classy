
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
	path('', views.index, name='index'),
	path('admin/', admin.site.urls),
	path('data', views.data, name='data'),
	path('data/<int:classy_id>/', views.log_detail, name='log_detail'),
	#path('register', views.register, name='register'),
	path('user_logout', views.user_logout, name='user_logout'),
	path('uploader', views.uploader, name='uploader'),
	path('search', views.search, name='search'),
	path('home', views.home, name='home'),
	path('test', views.test, name='test'),
	path('modi', views.modi, name='modi'),
	path('logs', views.logs, name='logs'),
	path('review', views.review, name='review'),
	path('exceptions', views.exceptions, name='exceptions'),
	path('log_list', views.log_list, name='log_list'),
]
