from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from classy.models import ClassificationReviewGroups, ClassificationReview
from classy.views.common import helper
from classy.forms import ClassificationLogForm

#Allow staff to review basic user changes, and accept/reject them
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
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