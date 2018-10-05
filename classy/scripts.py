import csv, re

from classy.models import * 
from classy.forms import *

options = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']


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
def create_thread(fs, filename, request, lock, th, threads, user):
    lock.acquire() 

    try: 
        uploaded_file_url = fs.url(filename)
        th.state = 'active'

        row_count = sum(1 for i in csv.reader(open(uploaded_file_url))) 
        row_count = int(row_count/100)
        if row_count <= 0:
            row_count = 1   
        reader = csv.DictReader(open(uploaded_file_url))
        counter = 0

        if set(['Datasource Description', 'Schema', 'Table Name', 'Column Name', 'Classification Name']).issubset(reader.fieldnames):    
            for row in reader:
                counter = counter + 1
                th.progress = str(counter//row_count)
                data_list = re.split(':', row['Datasource Description'])
                if not classification.objects.filter(
                schema__exact=row['Schema'], 
                table_name__exact=row['Table Name'], 
                column_name__exact=row['Column Name'], 
                datasource_description__exact=str.strip(data_list[3])):    
                    data = {}
                    data['classification_name'] = row['Classification Name']
                    data['schema'] = row['Schema']
                    data['table_name'] =  row['Table Name']
                    data['column_name'] = row['Column Name']
                    data['category'] = row['Category']
                    data['datasource_description'] = data_list[3]
                    data['created_by'] = user
                    data['state'] = 'Active'
                    form = ClassificationForm(data)
                    if form.is_valid():
                        tmp = form.save()
                        log_data = {}
                        log_data['classy'] = tmp.id
                        log_data['action_flag'] = 2
                        log_data['n_classification'] = row['Classification Name']
                        log_data['o_classification'] = row['Classification Name']
                        log_data['user_id'] = user
                        log_data['state'] = 'Active'
                        log_data['approved_by'] = 'N/a'
                        log_form = classificationLogForm(log_data)
                        if log_form.is_valid():
                            log_form.save()
                        else:
                            print('log form error')
                        if row['Classification Name'] != 'Unclassified':
                            exc_data = {}
                            exc_data['classy'] = tmp.id
                            exc_form = classificationExceptionForm(exc_data)
                            if exc_form.is_valid():
                                exc_form.save() 
                            else:
                                print('exception form error')
                    else:
                        print('Invalid value in form')
        else:
            #This is not a guardium report
            pass
    except Exception as e:
        print(e)        
    fs.delete(filename)
    threads.remove(th)
    lock.release()

