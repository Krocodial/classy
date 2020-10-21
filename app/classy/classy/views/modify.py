from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

import json

from classy.forms import ClassificationForm, ClassificationReviewForm
from classy.models import ClassificationReviewGroups, Application, Classification
from classy.views.common import helper, shared


#The search page POSTs to here via an AJAX call, this will auto-change values for staff, and create a review group for basic users.
#modifications will now auto-create logs if using the ClassificationForm
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
def modify(request):
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
            if index['classy'] in shared.untranslate:
                data['classification'] = shared.untranslate[index['classy']]
        if 'proty' in index:
            if index['proty'] in shared.untranslate:
                data['protected_type'] = shared.untranslate[index['proty']]
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