from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from background_task.models import Task

from classy.forms import UploadFileForm
from classy.models import ClassificationReviewGroups
from classy.views.common import helper


#Handles file uploads. Uploads file with progress bar, schedules a task to handle the file once uploaded. A thread spawned by the classy instance will handle this file upload. I might change this back to a cron job to allow multiple classy containers in the future for higher stability. I'll need to figure out a way to share file uploads cross pods though which I'm not too keen on for now. .
@login_required
@ratelimit(key='user', rate=helper.custom_rate, block=True, method='ALL')
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