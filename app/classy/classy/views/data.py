from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.views.common import helper, shared
from classy.models import ClassificationReviewGroups
from classy.forms import BasicSearch, AdvancedSearch

#Initial landing page for data table
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
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
        'translate': shared.translate,
        'ex_options': shared.ex_options,
        'ex_poptions': shared.ex_poptions,
        'advanced': advanced,
        'message': message,
        'result': result,
        'sizes': shared.sizes,
        'size': 10
        }
    return render(request, 'classy/data_tables.html', context)