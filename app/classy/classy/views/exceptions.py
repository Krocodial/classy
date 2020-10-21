from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.models import Classification, ClassificationLogs
from classy.views.common import helper

#Allows us to see what has been pre-classified before upload into this tool, for verification purposes
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
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