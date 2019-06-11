
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.dateparse import *
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.html import escape

from ratelimit.decorators import ratelimit

import threading, csv, json, random, os, difflib

from .models import ClassificationCount, Classification, ClassificationLogs, ClassificationReviewGroups, ClassificationReview
from .forms import *
from .scripts import calc_scheduler, upload
from .helper import query_constructor, role_checker

from background_task.models import Task

#if not Task.objects.filter(queue='counter').count() > 0:
#    calc_scheduler(repeat=300)


#To translate Classifications between the templates and the DB. (For database size optimization)
ex_options = ['Unclassified', 'Public', 'Confidential', 'Protected A', 'Protected B', 'Protected C']
options = ['UN', 'PU', 'CO', 'PA', 'PB', 'PC']
translate = {'UN': 'Unclassified', 'CO': 'Confidential', 'PU': 'Public', 'PE': 'Personal', 'PA': 'Protected A', 'PB': 'Protected B', 'PC': 'Protected C', '': ''}
untranslate = {'Unclassified': 'UN', 'Confidential': 'CO', 'Public': 'PU', 'Personal': 'PE', 'Protected A': 'PA', 'Protected B': 'PB', 'Protected C': 'PC'}
state_translate = {'A': 'Active', 'P': 'Pending', 'I': 'Inactive'}
flag_translate = {'0': 'Delete', '1': 'Modify', '2': 'Create'}


threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

@login_required
def debugg(request):
    if not request.user.is_staff:
        return redirect('classy:home')
    return JsonResponse(request.META) 
    #HttpResponse(request.META)

#Accessed from the home.html page
@login_required
def tutorial(request):
    return HttpResponse('coming soon...')
    if request.user.is_staff:
        return render(request, 'classy/tutorial.html')
    if request.user.is_authenticated:
        return render(request, 'classy/base_tutorial.html')

#Download search results from the search function
@login_required
def download(request):
    if not request.method == 'POST':
            return redirect('classy:home')
    form = AdvancedSearch(request.POST)
    if form.is_valid():
        if(form.cleaned_data['query'] != ''):
            value = form.cleaned_data['query']
            cols = Classification.objects.filter(column__icontains=value);
            tabs = Classification.objects.filter(table__icontains=value);
            schemas = Classification.objects.filter(schema__icontains=value);
            data = Classification.objects.filter(datasource__icontains=value);
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
            sql = Classification.objects.filter(column__icontains=co, table__icontains=tab, schema__icontains=sch, datasource__icontains=ds, classification__in=classi, state__in=stati);
            queryset = sql

        queryset = query_constructor(queryset, request.user)
        queryset = queryset.order_by('datasource', 'schema', 'table')
    
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Classification', 'Application', 'Datasource', 'Schema', 'Table', 'Column', 'Created', 'Creator', 'State', 'Masking instructions', 'Notes'])
        
        for tuple in queryset:
            writer.writerow([translate[tuple.classification], tuple.owner.acronym, tuple.datasource, tuple.schema, tuple.table, tuple.column, tuple.created, tuple.creator.first_name, state_translate[tuple.state], tuple.masking, tuple.notes])
        return response
    else:
        print(form.errors)

    return redirect('classy:index')

#Allow staff to review basic user changes, and accept/reject them
@login_required
def review(request):
    if not request.user.is_staff:
            return redirect('classy:home')
    num = ClassificationReviewGroups.objects.all().count()
    message = ''
    if request.method == 'POST':
        if 'response' in request.POST:
            message = request.POST['response']
        else:
            try:
                groupi = json.loads(request.POST['group'])
            except KeyError:
                return HttpResponseBadRequest()
            group_info = ClassificationReviewGroups.objects.get(id=groupi)
            user = group_info.user
            group_set = ClassificationReview.objects.filter(group__exact=groupi)
            if 'denied' in request.POST:
                den = json.loads(request.POST['denied'])
                for tup in group_set:
                    if str(tup.classy.id) in den:
                        continue
                    
                    log = {}
                    item = Classification.objects.get(id=tup.classy.id)
                    log['classy'] = item.pk
                    log['flag'] = tup.flag
                    log['user'] = user.pk
                    log['approver'] = request.user.pk
                
                    #modify
                    if tup.flag == 1:
                        log['classification'] = tup.classification
                        log['state'] = 'A'
                        form = ClassificationLogForm(log)
                        if form.is_valid():
                            item.classification = tup.classification
                            item.state='A'
                            item.save()
                            form.save()

                    #delete
                    elif tup.flag == 0:
                        log['classification'] = tup.classification
                        log['state'] = 'I'
                        form = ClassificationLogForm(log)
                        if form.is_valid():
                            item.state = 'I'
                            item.save()
                            form.save()
                    tup.delete()
                group_info.delete()
            else:
                group_set.delete()
                group_info.delete()
            response = {"status": 1, "message": "ok"}
            return JsonResponse(response)
        #return HttpResponse(json.dumps(reponse), content_type='application/json')
    queryset = ClassificationReview.objects.all()
    groups = ClassificationReviewGroups.objects.all()
    
    context = {'queryset': queryset, 'groups': groups, 'message': message, 'num': num, 'translate': translate}
    return render(request, 'classy/review.html', context)

#Allows us to see what has been pre-classified before upload into this tool, for verification purposes
@login_required
def exceptions(request):
    if not request.user.is_staff:
        return redirect('classy:index')        
    num = ClassificationReviewGroups.objects.all().count()
    form = BasicSearch(request.GET)

    if request.method == 'POST':
        if form.is_valid():
            value = form.cleaned_data['query']

        
            clas = ClassificationLogs.objects.filter(classification__icontains=value)
            prot = ClassificationLogs.objects.filter(protected_type__icontains=value)
            data = ClassificationLogs.objects.filter(classy__datasource__icontains=value)
            sche = ClassificationLogs.objects.filter(classy__schema__icontains=value)
            tabl = ClassificationLogs.objects.filter(classy__table__icontains=value)
            colu = ClassificationLogs.objects.filter(classy__column__icontains=value)
            user = ClassificationLogs.objects.filter(classy__creator__first_name__icontains=value)
            appo = ClassificationLogs.objects.filter(classy__owner__name__icontains=value)

            if value.isdigit():
                clas = ClassificationLogs.objects.filter(classy_id=int(value)) 

            queryset = prot | data | sche | tabl | colu | user | appo | clas
            
    else:
        queryset = ClassificationLogs.objects.all()
        
    queryset = queryset.filter(flag=2).exclude(classification='UN')
    permitted = query_constructor(Classification.objects.all(), request.user)
    permitted = permitted.values_list('pk', flat=True)
    queryset = queryset.filter(classy__in=permitted)

    page = 1
    if 'page' in request.GET:
        page = request.GET.get('page')
    queryset = queryset.order_by('-classy__created')
    paginator = Paginator(queryset, 50)
    query = paginator.get_page(page)
    form = BasicSearch()

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

    if 3 < current < paginator.num_pages - 2:
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

# List all of the Classification logs, filtered down to the Classification objects you are allowed to view. Searchable by Classification, flag, username, approver, and index
@login_required
def log_list(request):
    form = BasicSearch(request.GET)

    #middleware candidate
    num = ClassificationReviewGroups.objects.all().count()
    if form.is_valid():
        value = form.cleaned_data['query']

    
        clas = ClassificationLogs.objects.filter(classification__icontains=value)
        prot = ClassificationLogs.objects.filter(protected_type__icontains=value)
        data = ClassificationLogs.objects.filter(classy__datasource__icontains=value)
        sche = ClassificationLogs.objects.filter(classy__schema__icontains=value)
        tabl = ClassificationLogs.objects.filter(classy__table__icontains=value)
        colu = ClassificationLogs.objects.filter(classy__column__icontains=value)
        user = ClassificationLogs.objects.filter(classy__creator__first_name__icontains=value)
        appo = ClassificationLogs.objects.filter(classy__owner__name__icontains=value)

        if value.isdigit():
            clas = ClassificationLogs.objects.filter(classy_id=int(value)) 

        queryset = prot | data | sche | tabl | colu | user | appo | clas
        
    permitted = query_constructor(Classification.objects.all(), request.user)
    permitted = permitted.values_list('pk', flat=True)
    queryset = queryset.filter(classy__in=permitted)

    page = 1
    if 'page' in request.GET:
        page = request.GET.get('page')
    
    queryset = queryset.order_by('-time')

    paginator = Paginator(queryset, 50)
    query = paginator.get_page(page)

    form = BasicSearch()

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
            'flag_translate': flag_translate,
    }
    return render(request, 'classy/log_list.html', context)

#Shows all information known about a Classification object. History, variables, associated users, masking instructions.
@login_required
def log_detail(request, classy_id):
    num = ClassificationReviewGroups.objects.all().count()
    #try:
    fil = Classification.objects.filter(id=classy_id)
    queryset = query_constructor(fil, request.user)

    if queryset.count() == 1:
        obj = Classification.objects.get(id=classy_id)
        tup = ClassificationLogs.objects.filter(classy_id__exact=classy_id)

        prev = ClassificationLogs.objects.filter(classy_id__exact=classy_id).order_by('-id')[0]

    else:
        return redirect('classy:index')        
    if request.method == 'POST':
        if 'masking' in request.POST and 'notes' in request.POST:
            old_masking = obj.masking
            old_notes = obj.notes
            form = LogDetailMNForm(request.POST, instance=obj)
            if form.is_valid():
                if form.cleaned_data['masking'] != old_masking or form.cleaned_data['notes'] != old_notes:

                    log_data = {}
                    log_data['classy'] = obj.pk
                    log_data['flag'] = 1
                    log_data['classification'] = obj.classification 
                    log_data['protected_type'] = obj.protected_type
                    log_data['user'] = request.user.pk
                    log_data['state'] = 'A'
                    log_data['approver'] = request.user.pk
                    log_data['masking_change'] = form.cleaned_data['masking']
                    log_data['note_change'] = form.cleaned_data['notes']
                    log_data['previous_log'] = prev.pk
                    log_form = ClassificationFullLogForm(log_data)
                    if log_form.is_valid():
                        form.save()
                        log_form.save()

        elif 'classification' in request.POST and 'protected_type' in request.POST:
            old_clas = obj.classification
            old_prot = obj.protected_type
            form = LogDetailForm(request.POST, instance=obj)
            if form.is_valid():
                if form.cleaned_data['classification'] != old_clas or form.cleaned_data['protected_type'] != old_prot:

                    form = LogDetailForm(request.POST, instance=obj)
                    log_data = {}
                    log_data['classy'] = obj.pk
                    log_data['previous_log'] = prev.pk
                    log_data['flag'] = 1
                    log_data['classification'] = request.POST['classification']
                    log_data['protected_type'] = request.POST['protected_type']
                    log_data['user'] = request.user.pk
                    log_data['state'] = 'A'
                    log_data['approver'] = request.user.pk
                    log_form = ClassificationLogForm(log_data)

                    if form.is_valid() and log_form.is_valid():
                        form.save()
                        log_form.save()

    tup = tup.order_by('-time')

    form = LogDetailForm(initial={'classification': obj.classification, 'protected_type': obj.protected_type})

    context = {
        'form': form,
        'result': tup,
        'obj': obj,
        'num': num,
        'translate': translate,
        'state_translate': state_translate,
        'flag_translate': flag_translate,
    }
    return render(request, 'classy/log_details.html', context)

#The search page POSTs to here via an AJAX call, this will auto-change values for staff, and create a review group for basic users.
@login_required
def modi(request):
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
            new_group = ClassificationReviewGroups(user=request.user)
            new_group.save()

        for i in toModRed:
            try:
                ide = i['id']
                classy = i['classy']
            except:
                #invalid json obj
                continue

            tup = Classification.objects.get(id=ide)
            if tup.state == 'P':
                continue
            
            info = {}

            info['classy'] = tup.pk
            info['flag'] = 1
                        

            if request.user.is_staff:
                info['state'] = 'A'
                info['classification'] = untranslate[classy]
                info['user'] = request.user.pk
                info['approver'] = request.user.pk

                form = ClassificationLogForm(info)
                tup.classification = untranslate[classy]
                tup.state = 'A'
            
            else:
                info['group'] = new_group.pk
                info['classification'] = untranslate[classy]
                
                form = ClassificationReviewForm(info)
                tup.state = 'P'

            if form.is_valid():
                tup.save()
                form.save()
        for i in toDelRed:
            try:
                tup = Classification.objects.get(id=int(i))
            except:
                #invalid list of vals
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
                form = ClassificationLogForm(info)
                tup.state = 'I'

            else:
                info['group'] = new_group.pk
                info['classification'] = tup.classification
                form = ClassificationReviewForm(info)
                tup.state = 'P'

            if form.is_valid():
                tup.save()
                form.save()
        response = {'status': 1, 'message': 'ok'}
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return redirect('classy:data')

#Once a user makes a search in the data view handle the request. Just search all the features of our Classification objects to find even partial matches and return them. The call to query_constructor will filter out values the user is not allowed to view.
@login_required
def search(request):
    num = ClassificationReviewGroups.objects.all().count()
    if request.method == 'GET':
        form = AdvancedSearch(request.GET)
        if form.is_valid():
            value=''
            ds=''
            sch=''
            tab=''
            co=''
            classi=[]
            stati=[]

            value = form.cleaned_data['query']
            cols = Classification.objects.filter(column__icontains=value);
            tabs = Classification.objects.filter(table__icontains=value);
            schemas = Classification.objects.filter(schema__icontains=value);
            data = Classification.objects.filter(datasource__icontains=value);
            queryset = cols | tabs | schemas | data
 
            ds = form.cleaned_data['data_source']
            sch = form.cleaned_data['schema']
            tab = form.cleaned_data['table']
            col = form.cleaned_data['column']
            classi = form.cleaned_data['classi']
            stati = form.cleaned_data['stati']
            if len(stati) == 0:
                stati = ['A', 'P']
            if len(classi) == 0:
                classi = options                

            queryset2 = Classification.objects.filter(column__icontains=col, table__icontains=tab, schema__icontains=sch, datasource__icontains=ds, classification__in=classi, state__in=stati)

            queryset = queryset & queryset2
            queryset = query_constructor(queryset, request.user)
           
            mapping = {}
            pie_information = []
            for op in options:
                tmp = queryset.filter(classification=op).count()
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
            form = AdvancedSearch(initial={'size': size})
        
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
                'col': col,
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
            form = AdvancedSearch()
            context = {
                'num': num,
                'form': form,
                'message': 'Invalid search'
            }
            return render(request, 'classy/data_tables.html', context)
    return redirect('classy:index')

# serve up the EX gov template for dev purposes
@login_required
def gov_temp(request):
    return render(request, 'classy/gov_temp.html')
    
#A work in progress. Node tree displaying all of the information in the DB, drill-down is enabled. 
@login_required
def test(request):

    if request.method == 'POST':
        arr = request.POST['node'].split('/')
        if len(arr) < 2:
            response = {'status': 1, 'message': 'ok'}
            return HttpResponse(json.dumps(response), content_type='application/json')
        elif len(arr) == 2:
            schema = arr[0]
            ds = arr[1]
            tables = Classification.objects.filter(datasource=ds, schema=schema).values('table').distinct()
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
            columns = Classification.objects.filter(datasource=ds, schema=schema, table=table).values('column').distinct()
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

            tup = Classification.objects.get(datasource=ds, schema=schema, table=table, column=column)
            response = {'status': 2, 'message': 'ok', 'url': reverse('classy:data') + '/' + str(tup.id)}            
            return HttpResponse(json.dumps(response), content_type='application/json')
    sources = Classification.objects.values('datasource').distinct()
    schemas = Classification.objects.values('datasource', 'schema').distinct()
    tables = Classification.objects.values('schema', 'table', 'datasource').distinct()
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

# User is redirected here after authentication is complete via keycloak authentication server with a long, short-lived code. We exchange this code via an out-of-band REST call to the keycloak auth server for an access and refresh token. In the token is a list of permissions the user has, we check and set these via middleware. Once the token is verified we log the user in via a local session and give them a session cookie (they will never see the tokens so no risk of mishandling)
@ratelimit(key='ip', rate='6/m', method=['GET'], block=True)
def login_complete(request):
    try:
        redirect_uri = os.getenv('REDIRECT_URI') +  reverse('classy:login_complete')
        token = settings.OIDC_CLIENT.authorization_code(code=request.GET['code'], redirect_uri=redirect_uri)
        payload = settings.OIDC_CLIENT.decode_token(token['access_token'], settings.OIDC_CLIENT.certs()['keys'][0])
    
        request.session['access_token'] = token['access_token']
        request.session['refresh_token'] = token['refresh_token']

    except Exception as e:
        return HttpResponseForbidden('Invalid JWT token') 

    User = get_user_model()

    username = payload.get('sub')
    if username is None:
        return HttpResponseForbidden('Invalid payload')

    try:
        user, user_created = User.objects.get_or_create(username=username)
    except Exception as e:
        return HttpResponseForbidden('Error creating user') 

    if user_created:
        user.set_password(User.objects.make_random_password(length=40))
        user.email = payload.get('email')
        user.first_name = payload.get('name')
        user.last_name = payload.get('preferred_username')
        user.save()    
    elif user.email != payload.get('email'):
        user.email = payload.get('email')
        user.save()

    role_checker(user, payload, request)

    if not user.is_active:
        return HttpResponseForbidden('Contact the appropriate responsible party for permission. This access attempt has been logged.')
    login(request, user)
    return redirect('classy:home')
 
# If user is authenticated redirect to home, otherwise redirect to the auth url of the keycloak server. Here the user chooses how to authenticate (IDIR or local keycloak account). Once authenticated they are redirected to /login_complete
def index(request):
    if request.user.is_authenticated:
        return redirect('classy:home')

    auth_url = settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete'), scope='username email', state='alskdfjl;isiejf')
    return redirect(auth_url)   

#Home page once logged in. Pulls from ClassificationCounts to show statistics for the rows you are allowed to view (query_constructor)
@login_required
def home(request):

    #Just in case the appConfig fails
    #if not Task.objects.filter(queue='counter').count() > 0:
    #    calc_scheduler(repeat=180)

    data_cons = []
    mapping = {}

    for op in options:
        tmp = Classification.objects.filter(classification__exact=op)
        tmp = query_constructor(tmp, request.user)
        tmp = tmp.count()
        data_cons.append(tmp)
        mapping[op] = tmp
    num = ClassificationReviewGroups.objects.all().count()

    if query_constructor(Classification.objects.all(), request.user).count() == 0:
        empty = True
    else:
        empty = False

    label_cons = ex_options
    dates = []
    keys = {}
    

    for op in options:
        keys[op] = []

    for i in range(45):
        t = 44 - i
        d = timezone.now().date() - timezone.timedelta(days=t)
        dates.append(str(d))
        for clas, arr in keys.items():
            #print(clas, d)
            try:
                tmp = ClassificationCount.objects.get(date=d, classification=clas, user=request.user)
                arr.append(tmp.count)
            except ClassificationCount.DoesNotExist:
                #print('dne')
                pass
            except ClassificationCount.MultipleObjectsReturned:
                #print('too many')
                pass
    context = {
        #'queryset': queryset,
        'empty': empty,
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

#Handles file uploads. Uploads file with progress bar, schedules a task to handle the file once uploaded. A thread spawned by the classy instance will handle this file upload. I might change this back to a cron job to allow multiple classy containers in the future for higher stability. I'll need to figure out a way to share file uploads cross pods though which I'm not too keen on for now. .
@login_required
@ratelimit(key='user', rate='5/m', block=True, method=['POST'])
def uploader(request):
    spaces = re.compile(' ')
    if not request.user.is_staff:
        return redirect('classy:index')


    num = ClassificationReviewGroups.objects.all().count()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            '''
            form.save()
            context = {
                'status': '200',
                'form': UploadFileForm(),
                'num': num
            }
            return render(request, 'classy/jobs.html', context)
            '''
            f = form.cleaned_data['document']
            if f.name.endswith('.csv'):
                #inp = request.FILES['file']
                #name = spaces.sub('_', inp.name)
                #fs = FileSystemStorage()
                #filename = fs.save(name, inp)
                f = form.save() 
                
                upload(f.document.name, request.user.pk, priority=0, verbose_name=f.document.name, creator=request.user)

                '''         
                finfo = {}
                finfo['name'] = f.document
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
                '''
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
    tsks = Task.objects.filter(queue='upload')
    context = {'tsks': tsks, 'form': form, 'num': num}
    return render(request, 'classy/jobs.html', context)

#Initial landing page for data table
@login_required
@ratelimit(key='user', rate='10/m', block=True, method=['POST'])
def data(request):
    if not request.user.is_authenticated:
            return redirect('classy:index')

    num = ClassificationReviewGroups.objects.all().count()
    form = AdvancedSearch()
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

#Basic logout, this will end the local user session. However if the user is still authenticated with a SMSESSION cookie they will be automatically logged in again once directed to the index page. This is useful for immediately getting a new token pair from the keycloak server.
def user_logout(request):
    logout(request)
    return redirect('classy:index')

def health(request):
    return HttpResponse(200)
