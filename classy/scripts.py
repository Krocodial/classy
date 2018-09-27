from django.core import files
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.utils.dateparse import *
from django.core.files.storage import FileSystemStorage, Storage
from django.conf import settings

import re, io, csv, multiprocessing, time, signal, threading, queue, pytz

from .models import classification, classification_logs, classification_exception, classification_count
from .forms import ClassificationForm, permissionForm

options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']

def construct_query(request, queryset):
    if settings.BYPASS_AUTH:
        return classification.objects.all()

    user_queryset = classification.objects.all()

    return queryset & user_queryset

def calculate_count(logs, counts):  
    today = timezone.now().date()
    for classi, value in counts.items():
        new = classification_count(classification_name=classi, count=value, date=today)
        new.save()
    for i in range(1, 60):
        d = today - timezone.timedelta(days=i)
        dLogs = logs.filter(action_time__date=d)#action_time__gte=e, action_time__lte=s)
        dLogs.order_by('-action_time')
        for log in dLogs:
            if log.o_classification not in options:
                log.delete()
                continue        
            #If created
            if log.action_flag == 2:
                counts[log.o_classification] = counts[log.o_classification] - 1
            #Modify
            elif log.action_flag == 1:
                counts[log.o_classification] = counts[log.o_classification] + 1
                if log.n_classification != 'N/a':           
                    counts[log.n_classification] = counts[log.n_classification] -1
            #If deleted
            elif log.action_flag == 0:
                counts[log.o_classification] = counts[log.o_classification] + 1
            else:
                pass
        #print(counts)
        for classi, value in counts.items():
            new = classification_count(classification_name=classi, count=value, date=d-timezone.timedelta(days=1))
            new.save()


#File for generic scripts
class parent:
    def __init__(self, iden):
        children = []
        self.iden = iden 


def create_thread(request, lock, th, threads, user):
    spaces = re.compile(' ')
    lock.acquire()  

    inp = request.FILES['file']
    if(inp.closed):
                threads.remove(th)
                lock.release()
                return
    
    name = inp.name
    name = spaces.sub('_', name)
    fs = FileSystemStorage()
    filename = fs.save(name, inp)
    uploaded_file_url = fs.url(filename)
    th.state = 'active'

    try:
        
        row_count = sum(1 for i in csv.reader(open(uploaded_file_url))) 
        row_count = int(row_count/100)
        if row_count <= 0:
            row_count = 1   
        reader = csv.DictReader(open(uploaded_file_url))
        counter = 0
        for row in reader:
            counter = counter + 1
            th.progress = str(counter//row_count)
            data_list = re.split(':', row['Datasource Description'])

            if not classification.objects.filter(
            schema__exact=row['Schema'], 
            table_name__exact=row['Table Name'], 
            column_name__exact=row['Column Name'], 
            datasource_description=str.strip(data_list[3])):    
                data = {}
                data['classification_name'] = row['Classification Name']
                data['schema'] = row['Schema']
                data['table_name'] =  row['Table Name']
                data['column_name'] = row['Column Name']
                data['category'] = row['Category']
                data['datasource_description'] = data_list[3]
                data['created_by'] = user
                data['state'] = 'Active'
                try:
                    form = ClassificationForm(data)
                    if form.is_valid():
                        tmp = form.save()
                        log = classification_logs(classy_id = tmp.id, action_flag=2, n_classification=row['Classification Name'], o_classification=row['Classification Name'], user_id = user, state='Active', approved_by='N/a')
                        log.save()
                        if row['Classification Name'] != 'Unclassified':
                            e = classification_exception(classy=tmp)
                            e.save()
                    else:
                        print(form.errors)
                except Exception as e:
                    print(e)
        
        #f.close()
        fs.delete(filename)
        threads.remove(th)
        lock.release()
    except Exception as e:
        threads.remove(th)
        lock.release()
        print(e)


