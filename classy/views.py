from django.shortcuts import render

# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe

import threading, time, datetime
from pytz import timezone
import pytz
import json

from .forms import UploadFileForm, thread, advancedSearch, loginform#, Search
from .models import classification, classification_logs, classification_review, classification_review_groups
from .scripts import create_thread, parent, example

options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C'];
threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

def review(request):
	if not request.user.is_staff:
		return redirect('index')
	num = classification_review_groups.objects.all().count()
	message = ''
	if request.method == 'POST':
		if 'response' in request.POST:
			message = request.POST['response']
		else:
			try:
				den = json.loads(request.POST['denied'])
				groupi = json.loads(request.POST['group'])
				group_info = classification_review_groups.objects.get(id=groupi)
				user = group_info.user
				group_set = classification_review.objects.filter(group__exact=groupi)

				for row in group_set:
					item = classification.objects.get(id=row.classy.id)
					#modify
					if row.action_flag == 1:
						if row.classification_name in options and row.id not in den:
							log = classification_logs(classy = item, action_flag = 1, n_classification = row.classification_name, o_classification=row.o_classification, user_id = user, state='Active')
							item.classification_name = row.classification_name
							item.o_classification = row.o_classification

							log.save()
							item.save()
					#delete
					if row.action_flag == 0:
						if row.id not in den:
							log = classification_logs(classy = item, action_flag = 0, n_classification = 'N/a', o_classification = row.o_classification, user_id = user, state='Inactive')
							item.state = 'InActive'
	
							log.save()
							item.save()
				
					row.delete()

				group_info.delete()
				
				response = {'status': 1, 'message': 'ok'}
				return HttpResponse(json.dumps(response), content_type='application/json')
			except Exception as e:
				print(e)
				pass
			
	queryset = classification_review.objects.all();
	groups = classification_review_groups.objects.all();
	queryset = queryset.order_by('group', 'datasource_description', 'schema', 'table_name', 'column_name')	
	context = {'queryset': queryset, 'groups': groups, 'message': message, 'num': num}
	return render(request, 'classy/review.html', context)

def exceptions(request):
	if not request.user.is_staff:
		return redirect('index')

	context = {}
	return render(request, 'classy/exceptions.html', context)

def log_list(request):
	if not request.user.is_staff:
		return redirect('index')

	num = classification_review_groups.objects.all().count()
	logs = classification_logs.objects.all();
	logs = logs.order_by('-action_time')
	page = request.GET.get('page')
	paginator = Paginator(logs, 100)
	query = paginator.get_page(page)
	

	context = {
		'queryset': query,
		'num': num}
	return render(request, 'classy/log_list.html', context)

def log_detail(request, classy_id):
	if not request.user.is_authenticated:
		return redirect('index')
	num = classification_review_groups.objects.all().count()
	try:
		obj = classification.objects.get(id=classy_id)
		tup = classification_logs.objects.filter(classy_id__exact=classy_id)
		tup = tup.order_by('-action_time')
		context = {
			'result': tup,
			'obj': obj,
			'num': num
		}
	except classification.DoesNotExist:
		context = {}
	return render(request, 'classy/log_details.html', context)

def modi(request):
	if not request.user.is_authenticated:
		return redirect('index')

	if request.method == 'POST':
		toMod = request.POST['toMod']
		toModRed = json.loads(toMod)
		toDel = request.POST['toDel']
		toDelRed = json.loads(toDel)

		if len(toDelRed) == 0 and len(toModRed) == 0:
			return redirect('data')
		
		if not request.user.is_staff:
			new_group = classification_review_groups(user=request.user.username)
			new_group.save()
	
		for i in toModRed:
			if 'id' not in i:
				continue
			
			tup = classification.objects.get(id=i["id"])
			if request.user.is_staff:
				sql = classification_logs(
					classy = tup, 
					action_flag=1, 
					n_classification=i["classy"], 
					o_classification=tup.classification_name, 
					user_id = request.user.username, 
					state='Active')

				sql.save()
				tup.classification_name = i["classy"]
				tup.save()
			else:
				sql = classification_review(classy=tup,
					group=new_group, 
					classification_name=i["classy"], 
					schema=tup.schema,
					table_name=tup.table_name,
					column_name=tup.column_name,
					datasource_description=tup.datasource_description,
					action_flag=1,
					o_classification=tup.classification_name)

				sql.save()
				tup.state = 'Pending'
				tup.save()
					
		for i in toDelRed:
			tup = classification.objects.get(id=i)
			if request.user.is_staff:
				sql = classification_logs(
					classy = tup, 
					action_flag=0, 
					user_id = request.user.username, 
					state='Inactive')

				sql.save()
				tup.state = 'Inactive'
				tup.save()

			else:
				sql = classification_review(
					classy = tup, 
					group=new_group,
					schema=tup.schema,
					table_name=tup.table_name,
					column_name=tup.column_name,
					datasource_description=tup.datasource_description,
					action_flag=0, 
					o_classification=tup.classification_name)

				sql.save()
				tup.state = 'Pending'
				tup.save()

		response = {'status': 1, 'message': 'ok'}		
		return HttpResponse(json.dumps(response), content_type='application/json')
	else:
		return redirect('data')
		response = {'status': 0, 'message': 'not ok'}

def logs(request):
	if not request.user.is_authenticated:
		return redirect('index');
	num = classification_review_groups.objects.all().count()
	if id in request.GET:
		logs = classification_logs.objects.filter(classy_id__exact=request.GET['id'])
		context = {'logs': logs,
			'num': num}
		return render(request, 'classy/logs.html', context)
	else:
		return redirect('data')

def search(request):
	if not request.user.is_authenticated:
		return redirect('index')

	num = classification_review_groups.objects.all().count()
	if request.method == 'GET':
		form = advancedSearch(request.GET)
		if form.is_valid():
			value=ds=sch=tab=co=classi=''
			if(form.cleaned_data['query'] != ''):
				value = form.cleaned_data['query']
				cols = classification.objects.filter(column_name__contains=value);
				tabs = classification.objects.filter(table_name__contains=value);
				schemas = classification.objects.filter(schema__contains=value);
				data = classification.objects.filter(datasource_description__contains=value);
				queryset = cols | tabs | schemas | data
			else:
				ds = form.cleaned_data['data_source']
				sch = form.cleaned_data['schema']
				tab = form.cleaned_data['table']
				co = form.cleaned_data['column']
				classi = form.cleaned_data['classi']
				state = form.cleaned_data['stati']
				
				sql = classification.objects.filter(column_name__contains=co, table_name__contains=tab, schema__contains=sch, datasource_description__contains=ds, classification_name__contains=classi);	
				queryset = sql
			queryset = queryset.exclude(state__exact='Inactive')
			queryset = queryset.order_by('datasource_description', 'schema', 'table_name')
			size = 10
			if 'size' in request.GET:
				size = request.GET['size']
				page = 1;
			else:
				page = request.GET.get('page')

			paginator = Paginator(queryset, size)
			query = paginator.get_page(page)

			form = advancedSearch()
			
			context = {
				'num': num,
				'form': form,
				'queryset': query,
				'options': options,
				'query': value,
				'data_source': ds,
				'schema': sch,
				'table': tab,
				'column': co,
				'classi': classi,
				'size': size,
				'sizes': sizes
			}
			return render(request, 'classy/data_tables.html', context)
		else:
			form = advancedSearch()
			context = {
				'num': num,
				'form': form,
				'message': 'Invalid search'
			}
			return render(request, 'classy/data_tables.html', context)	
	return redirect(index)


def test(request):
	return render(request, 'classy/home.html', context)

def index(request):
	if request.user.is_authenticated:
		return redirect('home');
	
	if request.method == 'POST':	
		form = loginform(request.POST)
		if form.is_valid():
			usern = form.cleaned_data['username']
			passw = form.cleaned_data['password']
			user = authenticate(request, username=usern, password=passw)
			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				form = loginform()
				context = {
					'error_message': 'Not an authorized user',
					'form': form
				}
				return render(request, 'classy/index.html', context)
	
	form = loginform()
	context = {'form': form}
	return render(request, 'classy/index.html', context)

def home(request):
	if not request.user.is_authenticated:
		return redirect('index')
	queryset = classification_logs.objects.all().order_by('action_time')[:10]

	unclassified = classification.objects.filter(classification_name__exact='Unclassified').count()
	public = classification.objects.filter(classification_name__exact='PUBLIC').count()
	confidential = classification.objects.filter(classification_name__exact='CONFIDENTIAL').count()
	protected_a = classification.objects.filter(classification_name__exact='PROTECTED A').count()
	protected_b = classification.objects.filter(classification_name__exact='PROTECTED B').count()
	protected_c = classification.objects.filter(classification_name__exact='PROTECTED C').count()

	num = classification_review_groups.objects.all().count()

	data_cons = [unclassified, public, confidential, protected_a, protected_b, protected_c]
	label_cons = ["unclassified", 'public', 'confidential', 'protected a', 'protected b', 'protected c']
	context = {
		'queryset': queryset,
		'data_cons': data_cons,
		'label_cons': mark_safe(label_cons),
		'num': num
	}
	return render(request, 'classy/home.html', context);

def uploader(request):
	if not request.user.is_staff:
		return redirect('index')

	num = classification_review_groups.objects.all().count()
	for th in threads:
		th.uptime = str(time.time() - th.start)
		th.uptime = th.uptime[:4]

	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			f = request.FILES['file']
			if not f.name.endswith('.csv'):
				message = 'This is not a .csv file'
				form = UploadFileForm()
				context = {
					'form': form,
					'message': message,
					'num': num
				}
				return render(request, 'classy/jobs.html', context)
			th = thread(f.name, time.time(), 'pending', request.user.username)
			threads.append(th)
			t = threading.Thread(target=create_thread, args=(f, lock, th, threads, request.user.username))
			th.startdate = datetime.datetime.now()
			t.start()

		#if 'Myfile' in request.FILES: 
		#	inp = request.FILES['Myfile']
		#	th = thread(inp.name, time.time(), 'pending')
		#	threads.append(th)
		#	t = threading.Thread(target=create_thread, args=(inp, lock, th, threads, request.user.username))
		#	th.startdate = datetime.datetime.now()
		#	t.start()
	form = UploadFileForm()
	context = {'threads': threads, 'form': form, 'num': num}
	return render(request, 'classy/jobs.html', context)

def data(request):
	if not request.user.is_authenticated:
		return redirect('index')

	num = classification_review_groups.objects.all().count()
	form = advancedSearch()
	message = 'Results will appear after you have made a search'
	result = ''
	if 'success' in request.POST:
		result = 'success'
	if 'failure' in request.POST:
		result = 'failed'
	context = {
		'num': num,
		'form': form,
		'message': message,
		'result': result,
		'sizes': sizes,
		'size': 10
		}
	return render(request, 'classy/data_tables.html', context)

def user_logout(request):
	logout(request)
	return redirect('index')


