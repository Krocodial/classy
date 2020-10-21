from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.forms import LogDetailSubmitForm, LogDetailForm
from classy.models import ClassificationReviewGroups, ClassificationLogs, Classification
from classy.views.common import helper, shared

#Shows all information known about a Classification object. History, variables, associated users, masking instructions.
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
def log(request, classy_id):
    num = ClassificationReviewGroups.objects.all().count()

    queryset = helper.query_constructor(Classification.objects.all(), request.user)
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
        'translate': shared.translate,
        'state_translate': shared.state_translate,
        'flag_translate': shared.flag_translate,
    }
    return render(request, 'classy/log_details.html', context)