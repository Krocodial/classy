from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
from .helper import query_constructor
from classy.models import classification, classification_count, classification_logs, task, completed_task
from classy.forms import *

import csv, re, time, os, threading

options = ['CO', 'PU', 'UN', 'PA', 'PB', 'PC']
#options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']

translate = {'confidential': 'CO', 'public': 'PU', 'unclassified': 'UN', 'protected_a': 'PA', 'protected_b': 'PB', 'protected_c': 'PC'}

#Called once at web server initialization to check current counts for graphing purposes.
#@background(schedule=60, queue='calculate_count')
def calculate_count(user): 
    error = ''
    try: 
        counts = {}
        for op in options:
            count = query_constructor(classification.objects.filter(classification_name=op), user).count()
            counts[op] = count

        d = timezone.now().date()
        for classi, count in counts.items():
            try:
                cobj = classification_count.objects.get(date=d, classification_name=classi, user=user)
                cobj.count = count
                cobj.save()
            except classification_count.DoesNotExist:
                new = classification_count(classification_name=classi, count=count, date=d, user=user)
                new.save()
            except classification_count.MultipleObjectsReturned:
                pass
        permitted = query_constructor(classification.objects.all(), user)
        permitted = permitted.values_list('pk', flat=True)

        for i in range(60):
            d = timezone.now().date() - timezone.timedelta(days=i)
            logs = classification_logs.objects.filter(
                            time__startswith=d)
            logs = logs.filter(classy__in=permitted)

            for log in logs:
                if log.flag == 2:
                   counts[log.old_classification] = counts[log.old_classification] - 1 
                elif log.flag == 1:
                    counts[log.old_classification] = counts[log.old_classification] + 1
                    counts[log.new_classification] = counts[log.new_classification] - 1
                elif log.flag == 0:
                    counts[log.old_classification] = counts[log.old_classification] + 1
            d = timezone.now().date() - timezone.timedelta(days=i+1)
            for classi, count in counts.items():
                try:  
                    classification_count.objects.get(date=d, classification_name=classi, user=user)
                except classification_count.DoesNotExist:
                    new = classification_count(classification_name=classi, count=count, date=d, user=user)
                    new.save()
                except classification_count.MultipleObjectsReturned:
                    pass
    except Exception as e:
        error = e

    try:
        tmp = task.objects.get(queue='counter')
        run_at = tmp.run_at
        priority = tmp.priority
    except:
        run_at = timezone.now()
        priority = 0
    try:
        tmp = completed_task.objects.get(queue='counter')
        tmp.error = error
        tmp.run_at = run_at
        tmp.priority = priority
        tmp.save()
    except:
        info = {}
        info['name'] = 'counter'
        info['queue'] = 'counter'
        info['user'] = 1
        info['progress'] = 1
        info['error'] = error
        info['run_at'] = run_at
        info['priority'] = priority
        form = completed_taskForm(info)
        if form.is_valid():
            form.save()


def calc_scheduler(cthread):
    while True:
        try:
            tmp = task.objects.get(queue='counter')
            tmp.save()
            for user in User.objects.all():
                calculate_count(user)
        except task.DoesNotExist: 
            info = {}
            info['name'] = 'counter'
            info['queue'] = 'counter'
            info['user'] = 1
            info['priority'] = 0
            info['progress'] = 0
            form = taskForm(info)
            if form.is_valid():
                form.save()
            for user in User.objects.all():
                calculate_count(user)
        except task.MultipleObjectsReturned:
            tmp = task.objects.filter(queue='counter')
            tmp.delete()
        time.sleep(60)

#Called by 'uploader' in views to handle a file once uploaded.
#@background(schedule=10, queue='uploads')
def process_file(tsk):
    cinfo = {}
    filename = tsk.name
    user = tsk.user.id
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    try: 
        #uploaded_file_url = fs.url(filename)
        row_count = sum(1 for row in csv.DictReader(fs.open(filename, 'r')))
        reader = csv.DictReader(fs.open(filename, 'r'))
        itera = int(row_count/100)
        if itera == 0:
            itera = 1
        counter = 0
        notes = False
        masking_ins = False
        if set(['Datasource Description', 'Schema', 'Table Name', 'Column Name', 'Classification Name']).issubset(reader.fieldnames):    
            if 'notes' in reader.fieldnames:
                notes = True
            if 'masking instructions' in reader.fieldnames:
                masking_ins = True
            for row in reader:
                counter = counter + 1
                if counter%itera == 0:
                    prog = (counter/itera)*0.01
                    tsk.progress = prog
                    tsk.save()  
                data_list = re.split(':', row['Datasource Description'])
                database = data_list[3].strip()
                entCount = classification.objects.filter(
                        datasource__exact=database,
                        schema__exact=row['Schema'],
                        table__exact=row['Table Name'],
                        column__exact=row['Column Name']).count()
                if entCount < 1:
                    if notes:
                        note = row['notes'][:400]
                    else:
                        note = ''
                    if masking_ins:
                        masking = row['masking instructions'][:200]
                    else:
                        masking = ''

                    classy = row['Classification Name']
                    classy = classy.lower()
                    classy = re.sub(' ', '_', classy)
                    classy = translate[classy]

                    data = {}
                    data['classification_name'] = classy 
                    data['datasource'] = database
                    data['schema'] = row['Schema']
                    data['table'] =  row['Table Name']
                    data['column'] = row['Column Name']
                    data['creator'] = user
                    data['state'] = 'A'
                    data['masking'] = masking
                    data['notes'] = note
                    form = ClassificationForm(data)
                    if form.is_valid():
                        tmp = form.save()
                        log_data = {}
                        log_data['classy'] = tmp.id
                        log_data['flag'] = 2
                        log_data['new_classification'] = classy
                        log_data['old_classification'] = classy
                        log_data['user'] = user
                        log_data['state'] = 'A'
                        log_data['approver'] = user
                        log_form = classificationLogForm(log_data)
                        if log_form.is_valid():
                            log_form.save()
                        if classy != 'UN':
                            exc_data = {}
                            exc_data['classy'] = tmp.id
                            exc_form = classificationExceptionForm(exc_data)
                            if exc_form.is_valid():
                                exc_form.save() 
                            else:
                                #Exception form error
                                pass
                    else:
                        #Invalid value in form
                        pass
                elif entCount == 1:
                    classy = classification.objects.get(
                            datasource__exact=database,
                            schema__exact=row['Schema'],
                            table__exact=row['Table Name'],
                            column__exact=row['Column Name'])
                    MN = {}
                    MN['masking'] = classy.masking
                    MN['notes'] = classy.notes
                    #Once MN is assigned to the form the object values will also change
                    old_masking = classy.masking
                    old_notes = classy.notes
                    if masking_ins:
                        if len(row['masking instructions']) > len(classy.masking):
                            MN['masking'] = row['masking instructions'][:200]
                    if notes:
                        if len(row['notes']) > len(classy.notes):
                            MN['notes'] = row['notes'][:400]
                    form = logDetailMNForm(MN, instance=classy)
                    if form.is_valid() and (old_masking != MN['masking'] or old_notes != MN['notes']):
                        log_data = {'classy': classy.pk, 'flag': 1, 'new_classification': classy.classification_name, 'old_classification': classy.classification_name, 'user': user, 'state': 'A', 'approver': user, 'masking_change': form.cleaned_data['masking'], 'note_change': form.cleaned_data['notes']}
                        log_form = classificationFullLogForm(log_data)
                        if log_form.is_valid():
                            form.save()
                            log_form.save()
                else:
                    #Now we have encountered a critical issue with the upload function. Consider raising an error on the admin console or even sending an email. 
                    pass
        else:
            #This is not a guardium report
            pass
                
    except Exception as e:
        #Some error called e
        cinfo['error'] = e
    fs.delete(filename)
    cinfo['name'] = tsk.name
    cinfo['verbose_name'] = tsk.verbose_name
    cinfo['priority'] = tsk.priority
    cinfo['run_at'] = tsk.run_at
    cinfo['queue'] = tsk.queue
    #cinfo['error'] = error
    cinfo['user'] = user
    form = completed_taskForm(cinfo)
    if form.is_valid():
        form.save()

def upload(uthread):
    t = task.objects.filter(queue='uploads').count()
    while(t != 0):
        task_queue = task.objects.filter(queue='uploads').order_by('-priority', 'run_at')
        tsk = task_queue[0]
        uthread.name = tsk.name
        process_file(tsk)
        tsk.delete()
        t = task.objects.filter(queue='uploads').count()
    uthread.name = ''
    uthread.running=False
    return
        
