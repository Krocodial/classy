
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
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

from .models import *
from .forms import *
from .scripts import calc_scheduler, upload
from .helper import query_constructor

if settings.CONCURRENCY:
    uthread = thread(False)
    if not uthread.running:
        t = threading.Thread(target=upload, args=(uthread,), daemon=True)
        uthread.running = True
        t.start()

    cthread = thread(False)
    if not cthread.running:
        t = threading.Thread(target=calc_scheduler, args=(cthread,), daemon=True)
        cthread.running=True
        t.start()

#To translate classifications between the templates and the DB. (For database size optimization)
ex_options = ['UNCLASSIFIED', 'PUBLIC', 'CONFIDENTIAL', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']
options = ['UN', 'PU', 'CO', 'PA', 'PB', 'PC']
translate = {'UN': 'UNCLASSIFIED', 'CO': 'CONFIDENTIAL', 'PU': 'PUBLIC', 'PA': 'PROTECTED A', 'PB': 'PROTECTED B', 'PC': 'PROTECTED C'}
untranslate = {'UNCLASSIFIED': 'UN', 'CONFIDENTIAL': 'CO', 'PUBLIC': 'PU', 'PROTECTED A': 'PA', 'PROTECTED B': 'PB', 'PROTECTED C': 'PC'}
state_translate = {'A': 'Active', 'P': 'Pending', 'I': 'Inactive'}

threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]


#Accessed from the home.html page
def tutorial(request):
    if not request.user.is_authenticated:
        return redirect('classy:index')
    if request.user.is_staff:
        return render(request, 'classy/tutorial.html')
    if request.user.is_authenticated:
        return render(request, 'classy/base_tutorial.html')

#Download search results from the search function
def download(request):
    if not request.user.is_authenticated:
            return redirect('classy:index')
    if not request.method == 'POST':
            return redirect('classy:index')
    form = advancedSearch(request.POST)
    if form.is_valid():
        if(form.cleaned_data['query'] != ''):
            value = form.cleaned_data['query']
            cols = classification.objects.filter(column__icontains=value);
            tabs = classification.objects.filter(table__icontains=value);
            schemas = classification.objects.filter(schema__icontains=value);
            data = classification.objects.filter(datasource__icontains=value);
            queryset = cols | tabs | schemas | data
            queryset = queryset.exclude(state__exact='I')
        else:
            ds = form.cleaned_data['data_source']
            sch = form.cleaned_data['schema']
            tab = form.cleaned_data['table']
            co = form.cleaned_data['column']
            classi = form.cleaned_data['classi']
            stati = form.cleaned_data['stati']
            if len(stati) == 0:
                stati = ['A', 'P']
            if len(classi) == 0:
                classi = options
            sql = classification.objects.filter(column__icontains=co, table__icontains=tab, schema__icontains=sch, datasource__icontains=ds, classification_name__in=classi, state__in=stati);
            queryset = sql

        queryset = query_constructor(queryset, request.user)
        queryset = queryset.order_by('datasource', 'schema', 'table')
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow(['classification', 'datasource', 'schema', 'table', 'column', 'created', 'creator', 'state', 'masking instructions'])
        
        for tuple in queryset:
            writer.writerow([translate[tuple.classification_name], tuple.datasource, tuple.schema, tuple.table, tuple.column, tuple.created, tuple.creator, state_translate[tuple.state], tuple.masking])
        return response

    return redirect('classy:index')

#Allow staff to review basic user changes, and accept/reject them
def review(request):
    if not request.user.is_staff:
            return redirect('classy:index')
    num = classification_review_groups.objects.all().count()
    message = ''
    if request.method == 'POST':
        if 'response' in request.POST:
            message = request.POST['response']
        else:
            groupi = json.loads(request.POST['group'])
            group_info = classification_review_groups.objects.get(id=groupi)
            user = group_info.user
            group_set = classification_review.objects.filter(group__exact=groupi)
            if 'denied' in request.POST:
                den = json.loads(request.POST['denied'])
                for tup in group_set:
                    if str(tup.classy.id) in den:
                        continue
                    
                    log = {}
                    item = classification.objects.get(id=tup.classy.id)
                    log['classy'] = item.pk
                    log['flag'] = tup.flag
                    log['old_classification'] = tup.classy.classification_name
                    log['user'] = user.pk
                    log['approver'] = request.user.pk
                
                    #modify
                    if tup.flag == 1:
                        log['new_classification'] = tup.classification_name
                        log['state'] = 'A'
                        form = classificationLogForm(log)
                    if form.is_valid():
                        item.classification_name = tup.classification_name
                        item.state='A'
                        item.save()
                        form.save()

                    #delete
                    elif tup.flag == 0:
                        log['new_classification'] = tup.classification_name
                        log['state'] = 'I'
                        form = classificationLogForm(log)
                    if form.is_valid():
                        item.state = 'I'
                        item.save()
                        form.save()
                    tup.delete()
                group_info.delete()
            else:
                group_set.delete()
                group_info.delete()

        response = {'status': 1, 'message': 'ok'}
        return HttpResponse(json.dumps(response), content_type='application/json')
    queryset = classification_review.objects.all()
    groups = classification_review_groups.objects.all()
    
    context = {'queryset': queryset, 'groups': groups, 'message': message, 'num': num, 'translate': translate}
    return render(request, 'classy/review.html', context)

#Allows us to see what has been pre-classified before upload into this tool, for verification purposes
def exceptions(request):
    if not request.user.is_staff:
        return redirect('classy:index')        
    num = classification_review_groups.objects.all().count()
    form = basic_search(request.GET)

    if form.is_valid():
        value = form.cleaned_data['query']

        clas = classification_exception.objects.filter(classy__classification_name__icontains=value)
        ds = classification_exception.objects.filter(classy__datasource__icontains=value)
        sch = classification_exception.objects.filter(classy__schema__icontains=value)
        tab = classification_exception.objects.filter(classy__table__icontains=value)
        col = classification_exception.objects.filter(classy__column__icontains=value)


        if value.isdigit():
            clas_id = classifcation_exception.objects.filter(classy_id=int(value))
        else:
            clas_id = clas

        queryset = clas | sch | tab | col | clas_id | ds

        page = 1
        if 'page' in request.GET:
            page = request.GET.get('page')
        queryset = queryset.order_by('-classy__created')
        paginator = Paginator(queryset, 50)
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
            'last': last,    
            'translate': translate,
    }
        return render(request, 'classy/exceptions.html', context)

#Master log page, searchable
def log_list(request):
        if not request.user.is_staff:
            return redirect('classy:index')
        form = basic_search(request.GET)

        num = classification_review_groups.objects.all().count()

        if form.is_valid():
            value = form.cleaned_data['query']


            nclas = classification_logs.objects.filter(new_classification__icontains=value)
            oclas = classification_logs.objects.filter(old_classification__icontains=value)
            flag = classification_logs.objects.filter(flag__icontains=value)
            use = classification_logs.objects.filter(user__username__icontains=value)
            appro = classification_logs.objects.filter(approver__username__icontains=value)
            if value.isdigit():
                clas = classification_logs.objects.filter(classy_id=int(value)) 
            else:
                clas = nclas

            queryset = nclas | oclas | flag | use | appro | clas
            page = 1
            if 'page' in request.GET:
                page = request.GET.get('page')
            
            queryset = queryset.order_by('-time')

            paginator = Paginator(queryset, 50)
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
                    'last': last,
                    'translate': translate,
                    'state_translate': state_translate,
            }
            return render(request, 'classy/log_list.html', context)

#Shows all information known about a classification object. History, variables, associated users, masking instructions.
def log_detail(request, classy_id):
    if not request.user.is_staff:
            return redirect('classy:index')
    num = classification_review_groups.objects.all().count()
    try:
        obj = classification.objects.get(id=classy_id)
        tup = classification_logs.objects.filter(classy_id__exact=classy_id)
        tup = tup.order_by('-time')
        context = {
            'result': tup,
            'obj': obj,
            'num': num,
            'translate': translate,
            'state_translate': state_translate,
        }
    except classification.DoesNotExist:
        context = {}
    return render(request, 'classy/log_details.html', context)

#The search page POSTs to here, this will auto-change values for staff, and create a review group for basic users.
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
            new_group = classification_review_groups(user=request.user)
            new_group.save()

        for i in toModRed:
            if 'id' not in i:
                continue
            try: 
                tup = classification.objects.get(id=int(i["id"]))
            except Exception as e:
                continue
            if tup.state == 'P':
                continue
            
            info = {}

            info['classy'] = tup.pk
            info['flag'] = 1

            if request.user.is_staff:
                info['state'] = 'A'
                info['new_classification'] = untranslate[i['classy']]
                info['old_classification'] = tup.classification_name
                info['user'] = request.user.pk
                info['approver'] = request.user.pk

                form = classificationLogForm(info)
                tup.classification_name = untranslate[i["classy"]]
            
            else:
                info['group'] = new_group.pk
                info['classification_name'] = untranslate[i['classy']]
                
                form = classificationReviewForm(info)
                tup.state = 'P'

            if form.is_valid():
                tup.save()
                form.save()
        for i in toDelRed:
            try:
                tup = classification.objects.get(id=int(i))
            except Exception as e:
                continue
            if tup.state == 'P':
                continue
            info  = {}
            info['classy'] = tup.pk
            info['flag'] = 0

            if request.user.is_staff:
                info['state'] = 'I'
                info['user'] = request.user.pk
                info['approver'] = request.user.pk
                form = classificationLogForm(info)
                tup.state = 'I'

            else:
                info['group'] = new_group.pk
                info['classification_name'] = tup.classification_name
                form = classificationReviewForm(info)
                tup.state = 'P'

            if form.is_valid():
                tup.save()
                form.save()
        response = {'status': 1, 'message': 'ok'}
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return redirect('classy:data')

#Once a user makes a search in the data tab this handles that request
def search(request):
    if not request.user.is_authenticated:
        return redirect('classy:index')

    num = classification_review_groups.objects.all().count()
    if request.method == 'GET':
        form = advancedSearch(request.GET)
        if form.is_valid():
            value=ds=sch=tab=co=''
            classi=stati=[]

            value = form.cleaned_data['query']
            cols = classification.objects.filter(column__icontains=value);
            tabs = classification.objects.filter(table__icontains=value);
            schemas = classification.objects.filter(schema__icontains=value);
            data = classification.objects.filter(datasource__icontains=value);
            queryset = cols | tabs | schemas | data
 
            ds = form.cleaned_data['data_source']
            sch = form.cleaned_data['schema']
            tab = form.cleaned_data['table']
            co = form.cleaned_data['column']
            classi = form.cleaned_data['classi']
            stati = form.cleaned_data['stati']
            if len(stati) == 0:
                stati = ['A', 'P']
            if len(classi) == 0:
                classi = options                

            queryset2 = classification.objects.filter(column__icontains=co, table__icontains=tab, schema__icontains=sch, datasource__icontains=ds, classification_name__in=classi, state__in=stati)

            queryset = queryset & queryset2
            queryset = query_constructor(queryset, request.user)
           
            mapping = {}
            pie_information = []
            for op in options:
                tmp = queryset.filter(classification_name=op).count()
                pie_information.append(tmp)
                mapping[op] = tmp

            label_cons = ex_options
 
            queryset = queryset.order_by('datasource', 'schema', 'table', 'column')
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
                if tup.created - datetime.timedelta(days=14):
                    recent[tup.id] = True
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
                'recent': recent,
                'translate': translate,
                'untranslate': mark_safe(untranslate),
                'ex_options': ex_options,
                'label_cons': mark_safe(label_cons),
                'pie_information': pie_information,
            }
            return render(request, 'classy/data_tables.html', context)
        else:
            print(form.errors)
            form = advancedSearch()
            context = {
                'num': num,
                'form': form,
                'message': 'Invalid search'
            }
            return render(request, 'classy/data_tables.html', context)
    return redirect('classy:index')


def gov_temp(request):
    return render(request, 'classy/gov_temp.html')
    
#A work in progress. Node tree displaying all of the information in the DB, drill-down is enabled. 
def test(request):

    if request.method == 'POST':
        arr = request.POST['node'].split('/')
        if len(arr) < 2:
            response = {'status': 1, 'message': 'ok'}
            return HttpResponse(json.dumps(response), content_type='application/json')
        elif len(arr) == 2:
            schema = arr[0]
            ds = arr[1]
            tables = classification.objects.filter(datasource=ds, schema=schema).values('table').distinct()
            nodes = []
            links = []
            for each in tables:
                table = each['table']
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
            columns = classification.objects.filter(datasource=ds, schema=schema, table=table).values('column').distinct()
            nodes = []
            links = []
            for each in columns:
                name = each['column'] + '/' + table + '/' + schema + '/' + ds
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

            tup = classification.objects.get(datasource=ds, schema=schema, table=table, column=column)
            response = {'status': 2, 'message': 'ok', 'url': reverse('classy:data') + '/' + str(tup.id)}            
            return HttpResponse(json.dumps(response), content_type='application/json')
    sources = classification.objects.values('datasource').distinct()
    schemas = classification.objects.values('datasource', 'schema').distinct()
    tables = classification.objects.values('schema', 'table', 'datasource').distinct()
    trans = {}
    group = 0
    for each in sources:
        trans[each['datasource']] = group
        group = group + 1


    nodes = []
    links = [] 
    for each in sources:
        ds = each['datasource']
        nodes.append({'id': ds, 'group': trans[ds]})
    for each in schemas:
        nodes.append({'id': each['schema'] + '/' + each['datasource'], 'group': trans[each['datasource']]})

    for each in schemas:
        links.append({'source': each['schema'] + '/' + each['datasource'], 'target': each['datasource'], 'value': random.randint(1, 10)})

    context = {'nodes': mark_safe(nodes), 'links': mark_safe(links)}
    return render(request, 'classy/test.html', context)


#Main page, can authenticate users with siteminder or the default django authentication method. To alternate change the variable BYPASS_AUTH in settings.py
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

#Home page once logged in. Pulls from classification_counts to show statistics
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

    query_constructor(classification.objects.all(), request.user)
    
    label_cons = ex_options
    dates = []
    keys = {}
    

    if settings.PRES:
        mul = 20 
        for op in options:
            keys[op] = []
        for i in range(45):
            t = 44 - i
            d = timezone.now().date() - timezone.timedelta(days=t)
            dates.append(str(d))
            for clas, arr in keys.items():
                arr.append(random.randrange(i*mul, i*mul+1000)) 
 
    else:
        for op in options:
            keys[op] = []

        for i in range(45):
            t = 44 - i
            d = timezone.now().date() - timezone.timedelta(days=t)
            dates.append(str(d))
            for clas, arr in keys.items():
                #print(clas, d)
                try:
                    tmp = classification_count.objects.get(date=d, classification_name=clas)
                    arr.append(tmp.count)
                except classification_count.DoesNotExist:
                    #print('dne')
                    pass
                except classification_count.MultipleObjectsReturned:
                    #print('too many')
                    pass


    context = {
        #'queryset': queryset,
        'data_cons': data_cons,
        'label_cons': mark_safe(label_cons),
        'untranslate': mark_safe(untranslate),
        'num': num,
        'dates': dates,
        'unc': keys['UN'],
        'pub': keys['PU'],
        'conf': keys['CO'],
        'prota': keys['PA'],
        'protb': keys['PB'],
        'protc': keys['PC']
    }
    return render(request, 'classy/home.html', context);

#Handles file uploads. Uploads file with progress bar, schedules a task to handle the file once uploaded. A cron job pings the Task queue and takes care of the rest.
def uploader(request):
    spaces = re.compile(' ')
    if not request.user.is_staff:
        return redirect('classy:index')


    num = classification_review_groups.objects.all().count()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            if f.name.endswith('.csv'):
                inp = request.FILES['file']
                name = spaces.sub('_', inp.name)
                fs = FileSystemStorage()
                filename = fs.save(name, inp)
                                
                finfo = {}
                finfo['name'] = filename
                finfo['priority'] = 0
                finfo['queue'] = 'uploads'
                finfo['user'] = request.user.pk
                finfo['progress'] = 0
                
                form = taskForm(finfo)
                if form.is_valid():
                    form.save()
                if not settings.CONCURRENCY:
                    upload(thread(False))
                else:
                    if not uthread.running:
                        t = threading.Thread(target=upload, args=(uthread,))
                        uthread.running = True
                        t.start()                 

                context = {
                    'status': '200',
                    'form': UploadFileForm(),
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
                }
                return render(request, 'classy/jobs.html', context, status=422)
        else:
            context = {
                'form': UploadFileForm(),
                'num': num
            }
            return render(request, 'classy/jobs.html', context, status=423)
    
    form = UploadFileForm()
    tsks = task.objects.filter(queue='uploads')
    context = {'tsks': tsks, 'form': form, 'num': num}
    return render(request, 'classy/jobs.html', context)

#Initial page for data (could replace?)
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

#Basic logout(useless if siteminder is in use)
def user_logout(request):
    logout(request)
    return redirect('classy:index')

def health(request):
    return HttpResponse(200)
