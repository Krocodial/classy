from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
from .helper import query_constructor
from classy.models import Classification, ClassificationCount, ClassificationLogs
from classy.forms import *

from background_task import background
from background_task.models_completed import CompletedTask
import csv, re, time, os, threading

options = ['CO', 'PU', 'UN', 'PA', 'PB', 'PC']
#options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']

translate = {'confidential': 'CO', 'public': 'PU', 'unclassified': 'UN', 'protected_a': 'PA', 'protected_b': 'PB', 'protected_c': 'PC'}

#Called once at web server initialization to check current counts for graphing purposes.
#@background(schedule=60, queue='calculate_count')
def calculate_count(user):

    #Sort logs by date, +1 for create, -1 + 1 for mod?, -1 for del?
    #Get all pks, grab logs individually.  
    error = ''
    tmp = query_constructor(Classification.objects.all(), user).values_list('pk', flat=True)



@background(queue='counter')
def calc_scheduler():
    for user in User.objects.all():
        calculate_count(user)
    
    #print(CompletedTask.objects.all().order_by('run_at'))
    tsks = CompletedTask.objects.filter(queue='counter')[:5].values_list('id', flat=True)
    CompletedTask.objects.filter(queue='counter').exclude(pk__in=list(tsks)).delete()


#Called by 'uploader' in views to handle a file once uploaded.
#@background(schedule=10, queue='uploads')
def process_file(filename, user):
    cinfo = {}
    #filename = tsk.name
    #user = tsk.user.id
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
                #if counter%itera == 0:
                #    prog = (counter/itera)*0.01
                #    tsk.progress = prog
                #    tsk.save()  
                data_list = re.split(':', row['Datasource Description'])
                database = data_list[3].strip()
                entCount = Classification.objects.filter(
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
                    data['classification'] = classy 
                    data['protected_type'] = ''
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
                        log_data['classification'] = classy
                        log_data['protected_type'] = ''
                        log_data['user'] = user
                        log_data['state'] = 'A'
                        log_data['approver'] = user
                        log_form = ClassificationLogForm(log_data)
                        if log_form.is_valid():
                            log_form.save()
                    else:
                        #Invalid value in form
                        pass
                elif entCount == 1:
                    classy = Classification.objects.get(
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
                    form = LogDetailMNForm(MN, instance=classy)
                    if form.is_valid() and (old_masking != MN['masking'] or old_notes != MN['notes']):
                        log_data = {'classy': classy.pk, 'flag': 1, 'new_Classification': classy.Classification_name, 'old_Classification': classy.Classification_name, 'user': user, 'state': 'A', 'approver': user, 'masking_change': form.cleaned_data['masking'], 'note_change': form.cleaned_data['notes']}
                        log_form = ClassificationFullLogForm(log_data)
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
        print(e)
    fs.delete(filename)
    '''
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
    '''

@background(queue='upload')
def upload(filename, user):
    process_file(filename, user)
    '''
    while(t != 0):
        task_queue = task.objects.filter(queue='uploads').order_by('-priority', 'run_at')
        tsk = task_queue[0]
        uthread.name = tsk.name
        process_file(tsk)
        tsk.delete()
        t = task.objects.filter(queue='uploads').count()
    uthread.name = ''
    uthread.running=False
    '''
        
