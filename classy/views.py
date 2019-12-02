
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
from django.forms.models import model_to_dict

from ratelimit.decorators import ratelimit

import threading, csv, json, random, os, difflib, datetime

from .models import ClassificationCount, Classification, ClassificationLogs, ClassificationReviewGroups, ClassificationReview
from .forms import *
from .scripts import calc_scheduler, upload
from .helper import query_constructor, role_checker, filter_results, custom_rate

from background_task.models import Task

from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.middleware.csrf import get_token


#To translate Classifications between the templates and the DB. (For database size optimization)

options = [i[0] for i in Classification._meta.get_field('classification').flatchoices]
ex_options = [i[1] for i in Classification._meta.get_field('classification').flatchoices]

poptions = [i[0] for i in Classification._meta.get_field('protected_type').flatchoices]
ex_poptions = [i[1] for i in Classification._meta.get_field('protected_type').flatchoices]

#ex_options = ['Unclassified', 'Public', 'Confidential', 'Protected A', 'Protected B', 'Protected C']
#options = ['UN', 'PU', 'CO', 'PE']

translate = {'UN': 'Unclassified', 'CO': 'Confidential', 'PU': 'Public', 'PE': 'Personal', 'PA': 'Protected A', 'PB': 'Protected B', 'PC': 'Protected C', '': ''}
#untranslate = {'Unclassified': 'UN', 'Confidential': 'CO', 'Public': 'PU', 'Personal': 'PE', 'Protected A': 'PA', 'Protected B': 'PB', 'Protected C': 'PC'}
untranslate = {"Unclassified": "UN", "Confidential": "CO", "Public": "PU", "Personal": "PE", "Protected A": "PA", "Protected B": "PB", "Protected C": "PC"}
state_translate = {'A': 'Active', 'P': 'Pending', 'I': 'Inactive'}
flag_translate = {'0': 'Delete', '1': 'Modify', '2': 'Create'}


threads = []
lock = threading.Lock()
sizes = [10, 25, 50, 100]

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
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def download(request):
    if not request.method == 'POST':
            return redirect('classy:home')

    queryset = filter_results(request, request.POST)
    queryset = queryset.order_by('datasource', 'schema', 'table', 'column')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="classification_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Application', 'Classification', 'Protected Series', 'Datasource', 'Schema', 'Table', 'Column', 'Created', 'Creator', 'State', 'Masking instructions', 'Notes'])
   
    for tuple in queryset:
        if tuple.owner is not None:
            app = tuple.owner.acronym
        else:
            app = None
        writer.writerow([app, translate[tuple.classification], translate[tuple.protected_type], tuple.datasource, tuple.schema, tuple.table, tuple.column, tuple.created, tuple.creator.first_name, state_translate[tuple.state], tuple.masking, tuple.notes])
    return response

#Allow staff to review basic user changes, and accept/reject them
@login_required
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
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
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def exceptions(request):
    if not request.user.is_staff:
        return redirect('classy:index')        
    num = ClassificationReviewGroups.objects.all().count()
    form = BasicSearch(request.GET)

    if form.is_valid():
        value = form.cleaned_data['query']
    
        data = ClassificationLogs.objects.filter(classy__datasource__icontains=value)
        sche = ClassificationLogs.objects.filter(classy__schema__icontains=value)
        tabl = ClassificationLogs.objects.filter(classy__table__icontains=value)
        colu = ClassificationLogs.objects.filter(classy__column__icontains=value)
        user = ClassificationLogs.objects.filter(classy__creator__first_name__icontains=value)
        appo = ClassificationLogs.objects.filter(classy__owner__name__icontains=value)

        queryset = data | sche | tabl | colu | user | appo
        queryset = queryset.filter(flag__exact=2).exclude(classification__exact='UN')

    permitted = query_constructor(Classification.objects.all(), request.user)
    permitted = permitted.values_list('pk', flat=True)
    queryset = queryset.filter(classy__in=permitted)

    queryset = queryset.order_by('-classy__created')

    page = 1
    if 'page' in request.GET:
        page = request.GET.get('page')
    paginator = Paginator(queryset, 50)
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
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
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
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def log_detail(request, classy_id):
    num = ClassificationReviewGroups.objects.all().count()

    queryset = query_constructor(Classification.objects.all(), request.user)
    try:
        obj = queryset.get(id=classy_id)
        tup = ClassificationLogs.objects.filter(classy_id__exact=classy_id).order_by('-time')
    except:
        return redirect('classy:index')

    if request.method == 'POST' and request.user.is_staff:
        
        data = request.POST.copy()
        data['state'] = 'A'
        if data['classification'] in ['PU', 'UN']:
            data['protected_type'] = ''

        form = LogDetailSubmitForm(data, instance=obj)
        if form.is_valid() and form.has_changed():
            form.save(request.user.pk)
            form.save_m2m()

    form = LogDetailForm(initial=model_to_dict(obj))
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
#modifications will now auto-create logs if using the ClassificationForm
@login_required
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def modi(request):
    if request.method != 'POST':
        return redirect('classy:home')
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

    queryset = query_constructor(Classification.objects.all(), request.user)
    for index in toModRed:
        ide = index['id']
        try:
            tup = queryset.get(id__exact=ide)
        except:
            continue

        data = model_to_dict(tup)
   
        if tup.state == 'P':
            continue

        if 'classy' in index:
            if index['classy'] in untranslate:
                data['classification'] = untranslate[index['classy']]
        if 'proty' in index:
            if index['proty'] in untranslate:
                data['protected_type'] = untranslate[index['proty']]
        if 'newd' in index:
            if index['newd']:
                data['dependents'] = list(set(([dep.pk for dep in data['dependents']] or []) + ([int(newd) for newd in index['newd']] or [])))
            
        try:
            data['owner'] = Application.objects.get(id__exact=index['own']).pk
        except:
            pass  

        if data['classification'] in ['PU', 'UN']:
            data['protected_type'] = ''

        if request.user.is_staff:       
            data['state'] = 'A' 
            form = ClassificationForm(data, instance=tup)

            if form.is_valid() and form.has_changed():
                form.save(request.user.pk)
                
                #response = {'status': 0, 'message': 'error'}
                #return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            info = model_to_dict(tup)
            info['state'] = 'P'
            form = ClassificationForm(info, instance=tup)
            info['group'] = new_group.pk
            info['classy'] = tup.pk
            info['flag'] = 1
            review_form = ClassificationReviewForm(info)

            if form.is_valid() and review_form.is_valid():
                if form.has_changed():
                    form.save(request.user.pk, request.user.pk)
                    review_form.save()
            else:
                response = {'status': 0, 'message': 'error'}
                return HttpResponse(json.dumps(response), content_type='application/json')

    for i in toDelRed:
        try:
            tup = queryset.get(id=int(i))
        except:
            continue

        if tup.state == 'P':
            continue
        data = model_to_dict(tup)
        
        if request.user.is_staff:
            data['state'] = 'I'
            form = ClassificationForm(data, instance=tup)        
            if form.is_valid() and form.has_changed():
                form.save(request.user.pk)

        else:
            data['state'] = 'P'
            form = ClassificationForm(info, instance=tup)
            info['group'] = new_group.pk
            info['classy'] = tup.pk
            info['flag'] = 1
            review_form = ClassificationReviewForm(info)

            if form.is_valid() and review_form.is_valid():
                form.save(request.user.pk, request.user.pk)
                review_form.save()
            else:
                response = {'status': 0, 'message': 'error'}
                return HttpResponse(json.dumps(response), content_type='application/json')
        '''
        latest = ClassificationLogs.objects.filter(classy__exact=tup.pk).order_by('-time')[0]
        info  = model_to_dict(latest)
        info['classy'] = tup.pk
        info['flag'] = 0

        if request.user.is_staff:
            info['user'] = request.user.pk
            info['approver'] = request.user.pk
            info['state'] = 'I'

            data = info
            form = ClassificationLogForm(info)

        else:
            info['group'] = new_group.pk
            form = ClassificationReviewForm(info)
            data = {'state': 'P'}

        clas_form = ModifyForm(data, instance=tup)
        if form.is_valid() and clas_form.is_valid():
            clas_form.save()
            form.save()
        '''
    response = {'status': 1, 'message': 'ok'}
    return HttpResponse(json.dumps(response), content_type='application/json')

#Once a user makes a search in the data view handle the request. Just search all the features of our Classification objects to find even partial matches and return them. The call to query_constructor will filter out values the user is not allowed to view.
@login_required
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def search(request):
    if request.method != 'GET':
        return redirect('classy:home')
    num = ClassificationReviewGroups.objects.all().count()
    size = 10
    if 'size' in request.GET:
        if request.GET['size'] is not None:
            size = request.GET['size']

    queryset = filter_results(request, request.GET)
    queryset = queryset.order_by('datasource', 'schema', 'table', 'column')    


    nodeData = {}
    nodeData['datasets'] = []
    colors = [
        "#DBD5B5",
        "#46BFBD",
        "#FDB45C",
        "#949FB1",
        "#9FFFF5",
        "#7CFFC4",
        "#6ABEA7",
            ]

    data = []
    for op in options:
        count = queryset.filter(classification__exact=op).count()
        data.append(count)
    nodeData['datasets'].append({
            'data': data,
            'backgroundColor': colors})

    data = []
    for op in options:
        data.append(0)
    for pop in poptions:
        count = queryset.filter(protected_type__exact=pop).count()
        data.append(count)
    nodeData['datasets'].append({
            'data': data,
            'backgroundColor': colors})
    
    nodeData['labels'] = ex_options + ex_poptions

    clas_information = []       

    prot_information = []

    label_cons = ex_options
    if 'page' in request.GET:
        page = request.GET.get('page')
    else:
        page = 1
    paginator = Paginator(queryset, size)
    queryset = paginator.get_page(page)
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
    recent = {}
    for tup in queryset:
        if tup.created - datetime.timedelta(days=14):
            recent[tup.id] = True

    context = {
        'poptions': ex_options + ex_poptions,
        'num': num,
        'basic': BasicSearch(request.GET),
        'advanced': AdvancedSearch(request.GET),
        'queryset': queryset,
        'options': options,
        'size': size,
        'sizes': sizes,
        'prev': prev,
        'next': nex,
        'pags': pags,
        'first': first,
        'last': last,
        'recent': recent,
        'translate': translate,
        'untranslate': untranslate,
        'ex_options': ex_options,
        'ex_poptions': ex_poptions,
        'nodeData': nodeData,
        'modifyForm': ModifyForm()
    }
    return render(request, 'classy/data_tables.html', context)

# serve up the EX gov template for dev purposes
@login_required
def gov_temp(request):
    return render(request, 'classy/gov_temp.html')

# User is redirected here after authentication is complete via keycloak authentication server with a long, short-lived code. We exchange this code via an out-of-band REST call to the keycloak auth server for an access and refresh token. In the token is a list of permissions the user has, we check and set these via middleware. Once the token is verified we log the user in via a local session and give them a session cookie (they will never see the tokens so no risk of mishandling)
#@requires_csrf_token
@ratelimit(key='header:x-forwarded-for', rate=custom_rate, block=True)
def login_complete(request):
    try:
        redirect_uri = os.getenv('REDIRECT_URI') +  reverse('classy:login_complete')
        token = settings.OIDC_CLIENT.authorization_code(code=request.GET['code'], redirect_uri=redirect_uri)
        payload = settings.OIDC_CLIENT.decode_token(token['access_token'], settings.OIDC_CLIENT.certs()['keys'][0], options={"verify_signature": True, "verify_aud": True, "exp": True})
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
        return HttpResponseForbidden('Contact the appropriate party for permission. This access attempt has been logged.')
    login(request, user)
    return redirect('classy:home')
 
# If user is authenticated redirect to home, otherwise redirect to the auth url of the keycloak server. Here the user chooses how to authenticate (IDIR or local keycloak account). Once authenticated they are redirected to /login_complete
#@csrf_protect
def index(request):
    if request.user.is_authenticated:
        return redirect('classy:home')

    auth_url = settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete'))#, scope='username email', state='alskdfjl;isiejf'
    return redirect(auth_url)   

#Home page once logged in. Pulls from ClassificationCounts to show statistics for the rows you are allowed to view (query_constructor)
@login_required
def home(request):

    num = ClassificationReviewGroups.objects.all().count()


    queryset = query_constructor(Classification.objects.all(), request.user)
    nodeData = {}
    nodeData['datasets'] = []
    colors = [
            "#DBD5B5",
            "#46BFBD",
            "#FDB45C",
            "#949FB1",
            "#9FFFF5",
            "#7CFFC4",
            "#6ABEA7"]
    data = []
    for op in options:
        count = queryset.filter(classification__exact=op).count()
        data.append(count)
    for pop in poptions:
        data.append(0)
    nodeData['datasets'].append({
        'data': data,
        'backgroundColor': colors})

    data = []
    for op in options:
        data.append(0)
    for pop in poptions:
        count = queryset.filter(protected_type__exact=pop).count()
        data.append(count)
    nodeData['datasets'].append({
        'data': data,
        'backgroundColor': colors})

    nodeData['labels'] = ex_options + ex_poptions

    if queryset.count() == 0:
        empty = True
    else:
        empty = False

    label_cons = ex_options
    dates = []
    keys = {}
    lineDataset = []   
 
    colors = {
        'CO:PA': 'rgb(228,183,229)',
        'CO:PB': 'rgb(178,136,192)',
        'CO:PC': 'rgb(126,90,155)',
        'PE:PA': 'rgb(169,253,172)',
        'PE:PB': 'rgb(68,207,108)',
        'PE:PC': 'rgb(50,162,135)',
        'CO': 'rgb(163,88,212)',
        'PE': 'rgb(41,133,111)',
        'PU': 'rgb(70,191,189)',
        'UN': 'rgb(219,213,181)'
        }

    bak_colors = {
        'CO:PA': 'rgb(228,183,229,0.3)',
        'CO:PB': 'rgb(178,136,192,0.3)',
        'CO:PC': 'rgb(126,90,155,0.3)',
        'PE:PA': 'rgb(169,253,172,0.3)',
        'PE:PB': 'rgb(68,207,108,0.3)',
        'PE:PC': 'rgb(50,162,135,0.3)',
        'CO': 'rgb(163,88,212,0.3)',
        'PE': 'rgb(41,133,111,0.3)',
        'PU': 'rgb(70,191,189,0.3)',
        'UN': 'rgb(219,213,181,0.3)'
        }

    today = timezone.now().date()
    d = today - timezone.timedelta(days=29)
    new = ClassificationCount.objects.filter(date__gte=d, user=request.user)
    prev = ClassificationCount.objects.filter(date__lt=d, user=request.user).values('date').order_by('-date')
    

    initial = {}

    for op in options:
        if op in ['CO', 'PE']:
            for pop in poptions:
                keys[op+':'+pop] = []
                if prev.count() > 0:
                    tmp = ClassificationCount.objects.get(date=str(prev[0]['date']), classification=op, protected_type=pop, user=request.user)
                    initial[op+':'+pop] = tmp.count
                else: 
                    initial[op+':'+pop] = 0
        else:
            keys[op] = []
            if prev.count() > 0:
                tmp = ClassificationCount.objects.get(date=str(prev[0]['date']), classification=op, protected_type='', user=request.user)
                initial[op] = tmp.count
            else: 
                initial[op] = 0

    

    if new.count() > 0:
        for i in range(30):
            t = 29 - i
            d = today - timezone.timedelta(days=t)
            for clas, arr in keys.items():
                dic = clas.split(':')
                try:
                    if len(dic) > 1:
                        tmp = ClassificationCount.objects.get(date=d, classification=dic[0], protected_type=dic[1], user=request.user)
                    else:
                        tmp = ClassificationCount.objects.get(date=d, classification=dic[0], protected_type='', user=request.user)
                    arr.append(tmp.count)
                    initial[clas] = tmp.count
                except ClassificationCount.DoesNotExist:
                    arr.append(initial[clas])
                except ClassificationCount.MultipleObjectsReturned:
                    arr.append(initial[clas])
                    
    else:
        for key, array in keys.items():
            for i in range(30):
                array.append(initial[key])

    for i in range(30):
        t = 29 - i
        d = today - timezone.timedelta(days=t)
        dates.append(str(d))
    for clas, arr in keys.items():
        obj = {}
        dic = clas.split(':')
        if len(dic) > 1:
            obj['label'] = translate[dic[0]] + ' [' + dic[1] + ']' #translate[dic[1]]
        else:
            obj['label'] = translate[dic[0]]
        obj['borderColor'] = colors[clas]
        obj['backgroundColor'] = bak_colors[clas]
        obj['data'] = arr
        obj['fill'] = 'origin'
        lineDataset.append(obj)        

    context = {
        #'queryset': queryset,
        'poptions': ex_options + ex_poptions,
        'nodeData': nodeData,
        'empty': empty,
        'options': options,
        'label_cons': mark_safe(label_cons),
        'untranslate': untranslate,
        'num': num,
        'dates': dates,
        'keys': keys,
        'lineDataset': lineDataset,
    }
    return render(request, 'classy/home.html', context);

#Handles file uploads. Uploads file with progress bar, schedules a task to handle the file once uploaded. A thread spawned by the classy instance will handle this file upload. I might change this back to a cron job to allow multiple classy containers in the future for higher stability. I'll need to figure out a way to share file uploads cross pods though which I'm not too keen on for now. .
@login_required
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def uploader(request):
    spaces = re.compile(' ')
    if not request.user.is_staff:
        return redirect('classy:index')

    num = ClassificationReviewGroups.objects.all().count()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['document']
            if f.name.endswith('.csv'):
                f = form.save() 
                
                upload(f.document.name, request.user.pk, priority=0, verbose_name=f.document.name, creator=request.user)

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
@ratelimit(key='user', rate=custom_rate, block=True, method='ALL')
def data(request):
    if not request.user.is_authenticated:
            return redirect('classy:index')

    num = ClassificationReviewGroups.objects.all().count()
    basic = BasicSearch()
    advanced = AdvancedSearch()
    message = 'Results will appear after you have made a search'
    if 'message' in request.POST:
        message = request.POST['message']
    result = ''
    if 'success' in request.POST:
        result = 'success'
    if 'failure' in request.POST:
        result = 'failure'

    context = {
        'num': num,
        'basic': basic,
        'options': options,
        'translate': translate,
        'ex_options': ex_options,
        'ex_poptions': ex_poptions,
        'advanced': advanced,
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
