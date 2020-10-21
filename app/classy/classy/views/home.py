from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import render

from classy.models import Classification, ClassificationCount, ClassificationReviewGroups
from classy.views.common import helper, shared


#Home page once logged in. Pulls from ClassificationCounts to show statistics for the rows you are allowed to view (query_constructor)
@login_required
def home(request):

    num = ClassificationReviewGroups.objects.all().count()
	

    queryset = helper.query_constructor(Classification.objects.all(), request.user)
    nodeData = {}
    nodeData['datasets'] = []
    
    data = []
    for op in list(shared.options.keys()):
        count = queryset.filter(classification__exact=op).count()
        data.append(count)
    for pop in list(shared.poptions.keys()):
        data.append(0)
    nodeData['datasets'].append({
        'data': data,
        'backgroundColor': shared.colours})

    data = []
    for op in list(shared.options.keys()):
        data.append(0)
    for pop in list(shared.poptions.keys()):
        count = queryset.filter(protected_type__exact=pop).count()
        data.append(count)
    nodeData['datasets'].append({
        'data': data,
        'backgroundColor': shared.colours})

    nodeData['labels'] = list(shared.options.values()) + list(shared.poptions.values())

    if queryset.count() == 0:
        empty = True
    else:
        empty = False

    label_cons = list(shared.options.keys())
    dates = []
    keys = {}
    lineDataset = []   

    today = timezone.now().date()
    d = today - timezone.timedelta(days=29)
    new = ClassificationCount.objects.filter(date__gte=d, user=request.user)
    prev = ClassificationCount.objects.filter(date__lt=d, user=request.user).values('date').order_by('-date')
    

    initial = {}

    for op in list(shared.options.keys()):
        if op in ['CO', 'PE']:
            for pop in list(shared.poptions.keys()):
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
            obj['label'] = shared.translate[dic[0]] + ' [' + dic[1] + ']' #translate[dic[1]]
        else:
            obj['label'] = shared.translate[dic[0]]
        obj['borderColor'] = shared.border_colours[clas]
        obj['backgroundColor'] = shared.background_colours[clas]
        obj['data'] = arr
        obj['fill'] = 'origin'
        lineDataset.append(obj)        

    context = {
        #'queryset': queryset,
        'poptions': list(shared.options.values()) + list(shared.poptions.values()),
        'nodeData': nodeData,
        'empty': empty,
        'options': list(shared.options.keys()),
        'label_cons': mark_safe(label_cons),
        'untranslate': shared.untranslate,
        'num': num,
        'dates': dates,
        'keys': keys,
        'lineDataset': lineDataset,
    }
    return render(request, 'classy/home.html', context);