
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.utils.dateparse import *
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django import forms

import threading, time, csv, pytz, json, random

from .forms import *
from .models import *
from .scripts import *

options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C'];
threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

def tutorial(request):
    if not request.user.is_authenticated:
        return redirect('classy:index')
    if request.user.is_staff:
        return render(request, 'classy/tutorial.html')
    if request.user.is_authenticated:
        return render(request, 'classy/base_tutorial.html')

def download(request):
    if not request.user.is_authenticated:
            return redirect('classy:index')
    if not request.method == 'POST':
            return redirect('classy:index')
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

    return redirect('classy:index')

def review(request):
    if not request.user.is_staff:
            return redirect('classy:index')
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
                                log = classification_logs(classy = item, action_flag = 1, n_classification = tup.classification_name, o_classification=tup.o_classification, user_id = user, approved_by = request.user.username, state='Active')
                                item.classification_name = tup.classification_name
                                item.o_classification = tup.o_classification
                                item.state = 'Active'

                                log.save()
                                item.save()
                        #delete
                        elif tup.action_flag == 0:
                            item = classification.objects.get(id=tup.classy.id)
                            log = classification_logs(classy = item, action_flag = 0, n_classification = 'N/a', o_classification = tup.o_classification, user_id = user, approved_by = request.user.username, state='Inactive')
                            item.state = 'Inactive'

                            log.save()
                            item.save()
                        else:
                            pass
                            #print('unexpected value')
                        tup.delete()
                    group_info.delete()
                else:
                    group_set.delete()
                    group_info.delete()

                response = {'status': 1, 'message': 'ok'}
                return HttpResponse(json.dumps(response), content_type='application/json')
            except Exception as e:
                pass
    queryset = classification_review.objects.all();
    groups = classification_review_groups.objects.all();
    queryset = queryset.order_by('group', 'datasource_description', 'schema', 'table_name', 'column_name')
    
    context = {'queryset': queryset, 'groups': groups, 'message': message, 'num': num}
    return render(request, 'classy/review.html', context)

def exceptions(request):
    if not request.user.is_staff:
        return redirect('classy:index')        
    num = classification_review_groups.objects.all().count()
    form = basic_search(request.GET)

    if form.is_valid():
        value = form.cleaned_data['query']

        clas = classification_exception.objects.filter(classy__classification_name__icontains=value)
        sch = classification_exception.objects.filter(classy__schema__icontains=value)
        tab = classification_exception.objects.filter(classy__table_name__icontains=value)
        col = classification_exception.objects.filter(classy__column_name__icontains=value)


        if value.isdigit():
            clas_id = classifcation_exception.objects.filter(classy_id=int(value))
        else:
            clas_id = clas

        queryset = clas | sch | tab | col | clas_id

        page = 1
        if 'page' in request.GET:
            page = request.GET.get('page')
        queryset = queryset.order_by('-classy__creation_date')
        paginator = Paginator(queryset, 100)
        query = paginator.get_page(page)
        form = basic_search()
    
        prev = False
        nex = False
        first = False
        last = False
        current = int(page)
    
        if current > 1:
            prev = True
        if current < paginator.num_pages:
            nex = True
        pags = []

        if current > 3 and current < paginator.num_pages - 2:
            init = current -2
            for i in range(5):
                pags.append(init + i)
            first = True
            last = True
        elif current > 3:
            init = paginator.num_pages - 4
            for i in range(5):
                pags.append(init + i)
            first = True
        elif current < paginator.num_pages - 3:
            init = 1
            for i in range(5):
                pags.append(init + i)
            last = True
        context = {
        'queryset': query,
        'num': num,
            'form': form,
            'prev': prev,
            'next': nex,
            'pags': pags,
            'first': first,
            'last': last    
    }
        return render(request, 'classy/exceptions.html', context)

def log_list(request):
        if not request.user.is_staff:
            return redirect('classy:index')
        form = basic_search(request.GET)

        num = classification_review_groups.objects.all().count()

        if form.is_valid():
            value = form.cleaned_data['query']
            nclas = classification_logs.objects.filter(n_classification__icontains=value)
            oclas = classification_logs.objects.filter(o_classification__icontains=value)
            flag = classification_logs.objects.filter(action_flag__icontains=value)
            use = classification_logs.objects.filter(user_id__icontains=value)
            appro = classification_logs.objects.filter(approved_by__icontains=value)
            if value.isdigit():
                clas = classification_logs.objects.filter(classy_id=int(value)) 
            else:
                clas = nclas

            queryset = nclas | oclas | flag | use | appro | clas
            page = 1
            if 'page' in request.GET:
                page = request.GET.get('page')
            
            queryset = queryset.order_by('-action_time')

            paginator = Paginator(queryset, 100)
            query = paginator.get_page(page)

            form = basic_search()
      
            prev = False
            nex = False
            first = False
            last = False


            current = int(page)

            if current > 1:
                prev = True
            if current < paginator.num_pages:
                nex = True
            
            pags = []

            if current > 3 and current < paginator.num_pages - 2:
                init = current - 2
                for i in range(5):
                    pags.append(init + i)
                first = True
                last = True

            elif current > 3:
                init = paginator.num_pages - 4
                for i in range(5):
                    pags.append(init + i)
                first = True
            elif current < paginator.num_pages - 3:
                init = 1
                for i in range(5):
                    pags.append(init + i)
                last = True

            context = {
                    'num': num,
                    'form': form,
                    'queryset': query,
                    'prev': prev,
                    'next': nex,
                    'pags': pags,
                    'first': first,
                    'last': last
            }
            return render(request, 'classy/log_list.html', context)

def log_detail(request, classy_id):
    if not request.user.is_authenticated:
            return redirect('classy:index')
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
            return redirect('classy:index')
    if request.method == 'POST':
        if 'toMod' in request.POST:
            toMod = request.POST['toMod']
            toModRed = json.loads(toMod)
        else:
            toModRed = []
        if 'toDel' in request.POST:
            toDel = request.POST['toDel']
            toDelRed = json.loads(toDel)
        else:
            toDelRed = []

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
        return redirect('classy:data')

def search(request):
    if not request.user.is_authenticated:
        return redirect('classy:index')

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
                        
            prev = False
            nex = False
            first = False
            last = False
            current = int(page)

            if current > 1:
                prev = True
            if current < paginator.num_pages:
                nex = True
            pags = []

            if current > 3 and current < paginator.num_pages - 2:
                init = current - 2
                for i in range(5):
                    pags.append(init + i)
                first = True
                last = True
            elif current > 3:
                init = paginator.num_pages - 4
                for i in range(5):
                    pags.append(init + i)
                first = True
            elif current < paginator.num_pages - 3:
                init = 1
                for i in range(5):
                    pags.append(init + i)
                last = True
            else:
                init = 1
                for i in range(paginator.num_pages):
                    pags.append(init + i)
            form = advancedSearch(initial={'size': size})
        
            recent = {}
            for tup in query:
                if tup.creation_date - datetime.timedelta(days=14):
                    recent[tup.id] = True
                else:
                    recent[tup.id] = False
            

            context = {
                'num': num,
                'form': form,
                'queryset': query,
                'options': options,
                'query': value,
                'ds': ds,
                'sch': sch,
                'tab': tab,
                'co': co,
                'classi': classi,
                'stati': stati,
                'size': size,
                'sizes': sizes,
                'prev': prev,
                'next': nex,
                'pags': pags,
                'first': first,
                'last': last,
                'recent': recent
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
    return redirect('classy:index')


    

def test(request):

    if request.method == 'POST':
        arr = request.POST['node'].split('/')
        if len(arr) < 2:
            response = {'status': 1, 'message': 'ok'}
            return HttpResponse(json.dumps(response), content_type='application/json')
        elif len(arr) == 2:
            schema = arr[0]
            ds = arr[1]
            tables = classification.objects.filter(datasource_description=ds, schema=schema).values('table_name').distinct()
            nodes = []
            links = []
            for each in tables:
                table = each['table_name']
                name = table + '/' + schema + '/' + ds
                nodes.append({'id': name, 'group': 1})
                links.append({'source': name, 'target': schema + '/' + ds, 'value': random.randint(1, 5)}) 
            nodes.append({'id': schema + '/' + ds, 'group': 0})
            response = {'status': 1, 'message': 'ok', 'nodes': mark_safe(json.dumps(nodes)), 'links': mark_safe(json.dumps(links))}
            return HttpResponse(json.dumps(response), content_type='application/json')
        elif len(arr) == 3:
            table = arr[0]
            schema = arr[1]
            ds = arr[2]
            columns = classification.objects.filter(datasource_description=ds, schema=schema, table_name=table).values('column_name').distinct()
            nodes = []
            links = []
            for each in columns:
                name = each['column_name'] + '/' + table + '/' + schema + '/' + ds
                hlvl = table + '/' + schema + '/' + ds
                nodes.append({'id': name, 'group': 1})
                links.append({'source': name, 'target': hlvl, 'value': 0})
            nodes.append({'id': hlvl, 'group': 0})
            response = {'status': 1, 'message': 'ok', 'nodes': mark_safe(json.dumps(nodes)), 'links': mark_safe(json.dumps(links))}
            return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            column = arr[0]
            table = arr[1]
            schema = arr[2]
            ds = arr[3]

            tup = classification.objects.get(datasource_description=ds, schema=schema, table_name=table, column_name=column)
            response = {'status': 2, 'message': 'ok', 'url': reverse('classy:data') + '/' + str(tup.id)}            
            return HttpResponse(json.dumps(response), content_type='application/json')
    sources = classification.objects.values('datasource_description').distinct()
    schemas = classification.objects.values('datasource_description', 'schema').distinct()
    tables = classification.objects.values('schema', 'table_name', 'datasource_description').distinct()
    trans = {}
    group = 0
    for each in sources:
        trans[each['datasource_description']] = group
        group = group + 1


    nodes = []
    links = [] 
    for each in sources:
        ds = each['datasource_description']
        nodes.append({'id': ds, 'group': trans[ds]})
    for each in schemas:
        nodes.append({'id': each['schema'] + '/' + each['datasource_description'], 'group': trans[each['datasource_description']]})

    for each in schemas:
        links.append({'source': each['schema'] + '/' + each['datasource_description'], 'target': each['datasource_description'], 'value': random.randint(1, 10)})

    context = {'nodes': mark_safe(nodes), 'links': mark_safe(links)}
    return render(request, 'classy/test.html', context)



def index(request):
    if request.user.is_authenticated:
        return redirect('classy:home');
    
    #SiteMinder Authentication
    if settings.BYPASS_AUTH:
        pass
    else:

        user_name = request.META.get('HTTP_SM_UNIVERSALID')
        user_id = request.META.get('HTTP_SMGOV_USERIDENTIFIER')

        user_email = request.META.get('HTTP_SMGOV_USEREMAIL')
        user_display = request.META.get('HTTP_SMGOV_USERDISPLAYNAME')

        user_type = request.META.get('HTTP_SMGOV_USERTYPE')

        if user_type != 'Internal':
            form = loginform()
            context = {'form': form}
            return render(request, 'classy/index.html', context) 


        user = authenticate(request, username=user_name, password=user_id)
        if user is not None:
            login(request, user)
            return redirect('classy:home') 

    #First time login
    if request.method == 'POST':
        form = loginform(request.POST)
        if form.is_valid():
            if settings.BYPASS_AUTH:
                usern = form.cleaned_data['username']
            else:
                usern = user_name
            passw = form.cleaned_data['password']
            user = authenticate(request, username=usern, password=passw)
            if user is not None:

                if not settings.BYPASS_AUTH:
                    user.set_password(user_id)
                    user.email = user_email
                    user.last_name = user_display
                    user.save()
                login(request, user)
                return redirect('classy:home')
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
            return redirect('classy:index')
    data_cons = []
    mapping = {}

    for op in options:
        tmp = classification.objects.filter(classification_name__exact=op).count()
        data_cons.append(tmp)
        mapping[op] = tmp
    num = classification_review_groups.objects.all().count()

    label_cons = options    
    
    d = timezone.now().date() - timezone.timedelta(days=60)
    
    linee = classification_count.objects.filter(date__gte=d, classification_name__exact='Unclassified')

    if linee.count() < 60:
        vals = calculate_count(classification_logs.objects.filter(action_time__date__gte=d), mapping)
        vals = classification_count.objects.filter(date__gte=d)
    else:
        vals = linee


    dates = []
    dat = vals.order_by('date')
    for tuple in dat:
        if str(tuple.date) not in dates:
            dates.append(str(tuple.date))

    #print(dates)
    assoc = {}
    
    unclassified = []
    public = []
    confidential = []
    protected_a = []
    protected_b = []
    protected_c = []

    mul = 15
    for i in range(0, 60):
        unclassified.append(random.randrange(i*mul, i*mul+1000))
        public.append(random.randrange(i*mul, i*mul+1000))
        confidential.append(random.randrange(i*mul, i*mul+1000))
        protected_a.append(random.randrange(i*mul, i*mul+1000))
        protected_b.append(random.randrange(i*mul, i*mul+1000))
        protected_c.append(random.randrange(i*mul, i*mul+1000))
    #for i in dates:
    #   days.append(i)
    #for date in dates:
    #   print(date)
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

#@csrf_exempt
def uploader(request):
    if not request.user.is_staff:
        return redirect('classy:index')
    num = classification_review_groups.objects.all().count()
    for th in threads:
        th.uptime = str(timezone.now() - th.start)
        th.uptime = th.uptime[:7]

    if request.method == 'POST':
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
                    'num': num
                }
                return render(request, 'classy/jobs.html', context)
            else:
                message = 'This is not a .csv file'
                form = UploadFileForm()
                context = {
                    'form': form,
                    'message': message,
                    'num': num,
                    'threads': threads
                }
                return render(request, 'classy/jobs.html', context, status=422)
        else:
            context = {
                'form': UploadFileForm(),
                'threads': threads,
                'num': num
            }
            return render(request, 'classy/jobs.html', context, status=422)
    
    form = UploadFileForm()
    context = {'threads': threads, 'form': form, 'num': num}
    return render(request, 'classy/jobs.html', context)

def data(request):
    if not request.user.is_authenticated:
            return redirect('classy:index')

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
    return redirect('classy:index')


