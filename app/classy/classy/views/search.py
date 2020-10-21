from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.forms import BasicSearch, AdvancedSearch, ModifyForm
from classy.models import ClassificationReviewGroups
from classy.views.common import helper, shared



#Once a user makes a search in the data view handle the request. Just search all the features of our Classification objects to find even partial matches and return them. The call to query_constructor will filter out values the user is not allowed to view.
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
def search(request):
    if request.method != 'GET':
        return redirect('classy:home')
    num = ClassificationReviewGroups.objects.all().count()
    size = 10
    if 'size' in request.GET:
        if request.GET['size'] is not None:
            size = request.GET['size']

    queryset = helper.filter_results(request, request.GET)
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
    
    nodeData['labels'] = shared.ex_options + shared.ex_poptions

    clas_information = []       

    prot_information = []

    label_cons = shared.ex_options
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
        'translate': shared.translate,
        'untranslate': shared.untranslate,
        'ex_options': shared.ex_options,
        'ex_poptions': shared.ex_poptions,
        'nodeData': nodeData,
        'modifyForm': ModifyForm()
    }
    return render(request, 'classy/data_tables.html', context)