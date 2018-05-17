from django.shortcuts import render

# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.dateparse import *

import threading, time, csv#, datetime
#from pytz import timezone
import pytz
import json, random
#from datetime import datetime, timedelta

from .forms import UploadFileForm, thread, advancedSearch, loginform#, Search
from .models import classification, classification_exception, classification_logs, classification_review, classification_review_groups, classification_count
from .scripts import create_thread, parent, example, calculate_count

options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C'];
threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

def download(request):
	if not request.user.is_authenticated:
		return redirect('index')
	if not request.method == 'POST':
		return redirect('index')
	form = advancedSearch(request.POST)
	if form.is_valid():
		if(form.cleaned_data['query'] != ''):
			value = form.cleaned_data['query']
			cols = classification.objects.filter(column_name__icontains=value);
			tabs = classification.objects.filter(table_name__icontains=value);
			schemas = classification.objects.filter(schema__icontains=value);
			data = classification.objects.filter(datasource_description__icontains=value);
			queryset = cols | tabs | schemas | data
			queryset = queryset.exclude(state__exact='Inactive')
		else:
			ds = form.cleaned_data['data_source']
			sch = form.cleaned_data['schema']
			tab = form.cleaned_data['table']
			co = form.cleaned_data['column']
			classi = form.cleaned_data['classi']
			stati = form.cleaned_data['stati']
			if len(stati) == 0:
				stati = ['Active', 'Pending']
			if len(classi) == 0:
				classi = options
			sql = classification.objects.filter(column_name__icontains=co, table_name__icontains=tab, schema__icontains=sch, datasource_description__icontains=ds, classification_name__in=classi, state__in=stati);
			queryset = sql
		queryset = queryset.order_by('datasource_description', 'schema', 'table_name')
	
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="report.csv"'

		writer = csv.writer(response)
		writer.writerow(['classification', 'schema', 'table', 'column', 'category', 'datasource', 'creation date', 'created by', 'state'])
		
		for tuple in queryset:
			writer.writerow([tuple.classification_name, tuple.schema, tuple.table_name, tuple.column_name, tuple.category, tuple.datasource_description, tuple.creation_date, tuple.created_by, tuple.state])
		return response

	'''
		file_path = os.path.join(settings.MEDIA_ROOT, path)
		if os.path.exists(file_path):
			with open(file_path, 'rb') as fh:
				response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
				response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
				return response
		raise Http404
	'''
	return redirect('index')

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
				groupi = json.loads(request.POST['group'])
				group_info = classification_review_groups.objects.get(id=groupi)
				user = group_info.user
				group_set = classification_review.objects.filter(group__exact=groupi)
				if 'denied' in request.POST:
					den = json.loads(request.POST['denied'])
					for tup in group_set:
						if str(tup.classy.id) in den:
							pass
						#modify
						elif tup.action_flag == 1:
							if tup.classification_name in options:

								item = classification.objects.get(id=tup.classy.id)
								log = classification_logs(classy = item, action_flag = 1, n_classification = tup.classification_name, o_classification=tup.o_classification, user_id = user, state='Active')
								item.classification_name = tup.classification_name
								item.o_classification = tup.o_classification
								item.state = 'Active'

								log.save()
								item.save()
						#delete
						elif tup.action_flag == 0:
							item = classification.objects.get(id=tup.classy.id)
							log = classification_logs(classy = item, action_flag = 0, n_classification = 'N/a', o_classification = tup.o_classification, user_id = user, state='Inactive')
							item.state = 'Inactive'

							log.save()
							item.save()
						else:
							print('unexpected value')


						tup.delete()

					group_info.delete()

				else:
					group_set.delete()
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
	try:
		num = classification_review_groups.objects.all().count()
		queryset = classification_exception.objects.all().order_by('-classy__creation_date')
		if 'page' in request.GET:
			page = request.GET.get('page')
		else: 
			page = 1
		paginator = Paginator(queryset, 100)
		query = paginator.get_page(page)
	except Exception as e:
		print(e)
	context = {
		'queryset': query,
		'num': num
		
	}
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
					state='Active',
					approved_by='N/a')

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
					state='Inactive',
					approved_by='N/a')

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
			value=ds=sch=tab=co=''
			classi=stati=[]
			if(form.cleaned_data['query'] != ''):
				value = form.cleaned_data['query']
				cols = classification.objects.filter(column_name__icontains=value);
				tabs = classification.objects.filter(table_name__icontains=value);
				schemas = classification.objects.filter(schema__icontains=value);
				data = classification.objects.filter(datasource_description__icontains=value);
				queryset = cols | tabs | schemas | data
				queryset = queryset.exclude(state__exact='Inactive')
			else:
				ds = form.cleaned_data['data_source']
				sch = form.cleaned_data['schema']
				tab = form.cleaned_data['table']
				co = form.cleaned_data['column']
				classi = form.cleaned_data['classi']
				stati = form.cleaned_data['stati']
				if len(stati) == 0:
					stati = ['Active', 'Pending']
				if len(classi) == 0:
					classi = options
				#if len(classi) == 0:
				#	classi = []
				sql = classification.objects.filter(column_name__icontains=co, table_name__icontains=tab, schema__icontains=sch, datasource_description__icontains=ds, classification_name__in=classi, state__in=stati);
				queryset = sql
			queryset = queryset.order_by('datasource_description', 'schema', 'table_name')
			size = 10
			if 'size' in request.GET:
				size = request.GET['size']
			if 'page' in request.GET:
				page = request.GET.get('page')
			else:
				page = 1
			paginator = Paginator(queryset, size)
			query = paginator.get_page(page)

			form = advancedSearch(initial={'size': size})
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
				'stati': stati,
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
	data_cons = []
	mapping = {}

	for op in options:
		tmp = classification.objects.filter(classification_name__exact=op).count()
		data_cons.append(tmp)
		mapping[op] = tmp
	'''
	unclassified = classification.objects.filter(classification_name__exact='Unclassified').count()
	public = classification.objects.filter(classification_name__exact='PUBLIC').count()
	confidential = classification.objects.filter(classification_name__exact='CONFIDENTIAL').count()
	protected_a = classification.objects.filter(classification_name__exact='PROTECTED A').count()
	protected_b = classification.objects.filter(classification_name__exact='PROTECTED B').count()
	protected_c = classification.objects.filter(classification_name__exact='PROTECTED C').count()
	'''
	num = classification_review_groups.objects.all().count()

	#data_cons = [unclassified, public, confidential, protected_a, protected_b, protected_c]
	label_cons = options#["unclassified", 'public', 'confidential', 'protected a', 'protected b', 'protected c']

	#Line Graph
	d = datetime.datetime.now() - datetime.timedelta(days=10)
	#d = timezone.now().date() - timedelta(days=14)
	linee = classification_count.objects.filter(date__gte=d)

	if linee.count() < 10:
		vals = calculate_count(classification_logs.objects.filter(action_time__gte=d), mapping)
		vals = classification_count.objects.filter(date__gte=d)
	else:
		vals = linee


	dates = []
	dat = vals.order_by('date')
	for tuple in dat:
		if str(tuple.date) not in dates:
			dates.append(str(tuple.date))
	print(dates)
	assoc = {}
	'''
	unclassified = vals.filter(classification_name__exact='Unclassified').order_by('date')
	public = vals.filter(classification_name__exact='PUBLIC').order_by('date')
	confidential = vals.filter(classification_name__exact='CONFIDENTIAL').order_by('date')
	protected_a = vals.filter(classification_name__exact='PROTECTED A').order_by('date')
	protected_b = vals.filter(classification_name__exact='PROTECTED B').order_by('date')
	protected_c = vals.filter(classification_name__exact='PROTECTED C').order_by('date')
	'''
	unclassified = []
	public = []
	confidential = []
	protected_a = []
	protected_b = []
	protected_c = []

	for i in range(0, 10):
		unclassified.append(random.randrange(i, i+1000))
		public.append(random.randrange(i, i+1000))
		confidential.append(random.randrange(i, i+1000))
		protected_a.append(random.randrange(i, i+1000))
		protected_b.append(random.randrange(i, i+1000))
		protected_c.append(random.randrange(i, i+1000))
	#for i in dates:
	#	days.append(i)
	#for date in dates:
	#	print(date)
		#days.append(date.day)

	context = {
		#'queryset': queryset,
		'data_cons': data_cons,
		'label_cons': mark_safe(label_cons),
		'num': num,
		'dates': dates,
		'unc': unclassified,
		'pub': public,
		'conf': confidential,
		'prota': protected_a,
		'protb': protected_b,
		'protc': protected_c
	}
	return render(request, 'classy/home.html', context);

@csrf_exempt
def uploader(request):
	if not request.user.is_staff:
		return redirect('index')
	num = classification_review_groups.objects.all().count()
	for th in threads:
		th.uptime = str(timezone.now() - th.start)
		#time.time() - th.start)
		th.uptime = th.uptime[:7]

	#if request.method == 'POST':
	try:
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			f = form.cleaned_data['file']
			if f.name.endswith('.csv'):
				th = thread(f.name, timezone.now(), 'pending', request.user.username)
				threads.append(th)
				t = threading.Thread(target=create_thread, args=(request, lock, th, threads, request.user.username))
				th.startdate = timezone.now()
				t.start()
				context = {
					'status': '200',
					'form': UploadFileForm(),
					'threads': threads,
				}
				return render(request, 'classy/jobs.html', context)
			else:
				message = 'This is not a .csv file'
				form = UploadFileForm()
				context = {
					'form': form,
					'message': message,
					'num': num,
					'status': '422',
					'threads': threads
				}
				return render(request, 'classy/jobs.html', context)
			'''
			th = thread(f.name, timezone.now(), 'pending', request.user.username)
			#time.time()
			threads.append(th)
			t = threading.Thread(target=create_thread, args=(f, lock, th, threads, request.user.username))
			th.startdate = timezone.now()
			#th.startdate = datetime.datetime.now()
			t.start()
			'''
		else:
			context = {
				'status': '422',
				'form': UploadFileForm(),
				'threads': threads
			}
			return render(request, 'classy/jobs.html', context)
	except Exception as e:
		print(e)
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


