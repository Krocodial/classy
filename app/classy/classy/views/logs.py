from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.forms import BasicSearch
from classy.models import ClassificationReviewGroups, ClassificationLogs
from classy.views.common import helper, shared


# List all of the Classification logs, filtered down to the Classification objects you are allowed to view. Searchable by Classification, flag, username, approver, and index
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
def logs(request):
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
        
    permitted = helper.query_constructor(Classification.objects.all(), request.user)
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
            'translate': shared.translate,
            'state_translate': shared.state_translate,
            'flag_translate': shared.flag_translate,
    }
    return render(request, 'classy/log_list.html', context)