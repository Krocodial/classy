from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .helper import query_constructor
from classy.models import Classification, ClassificationCount, ClassificationLogs
from classy.forms import *

from background_task import background
from background_task.models_completed import CompletedTask
import csv, re, time, os, threading

options = [i[0] for i in Classification._meta.get_field('classification').flatchoices]
ex_options = [i[1] for i in Classification._meta.get_field('classification').flatchoices]

poptions = [i[0] for i in Classification._meta.get_field('protected_type').flatchoices] + ['']
ex_poptions = [i[1] for i in Classification._meta.get_field('protected_type').flatchoices]

translate = {'confidential': 'CO', 'public': 'PU', 'unclassified': 'UN', 'protected_a': 'PA', 'protected_b': 'PB', 'protected_c': 'PC', 'personal': 'PE'}

#Called once at web server initialization to check current counts for graphing purposes.
#@background(schedule=60, queue='calculate_count')
def calculate_count(user):

    #Sort logs by date, +1 for create, -1 + 1 for mod?, -1 for del?
    #Get all pks, grab logs individually.  
    error = ''
    tmp = query_constructor(Classification.objects.all(), user).values_list('pk', flat=True)
    
    logs = ClassificationLogs.objects.filter(classy__in=tmp).order_by('time')

    if tmp.count() > 0:

        previous = ''   
        mapping = {}
        for op in options:
            for pop in poptions:
                mapping[op + ':' + pop] = 0

        #Find previous classification of modified tuples. 
        minus = {}
        for key in tmp:
            classy_logs = logs.filter(classy__exact=key).order_by('id')
            previous = ''
            for log in classy_logs:
                date = log.time.date()
                if date not in minus:
                    tmp = {}
                    for op in options:
                        for pop in poptions:
                            tmp[op + ':' + pop] = 0
                    minus[date] = tmp
                key = log.classification + ':' + log.protected_type
                if log.flag == 0:    
                    minus[date][key] = minus[date][key] + 1
                elif log.flag == 1:
                    minus[date][previous] = minus[date][previous] + 1
                previous = key

        current = logs[0].time.date()
        for log in logs:
            date = log.time.date()
            if date != current:
                for key in mapping:
                    try:
                        mapping[key] = mapping[key] - minus[date][key]
                    except KeyError:
                        pass
                        #Just means no modifications or deletions for that key on that date
                for key, value in mapping.items():
                    dic = key.split(':')
                    if dic[1]:
                        protected_type = dic[1]
                    else:
                        protected_type = ''
                    data = {
                        'classification': dic[0], 
                        'protected_type': protected_type, 
                        'count': value, 
                        'date': current, 
                        'user': user.pk}
                    try:
                        item = ClassificationCount.objects.get(
                            date__exact=current,
                            classification__exact=dic[0],
                            protected_type__exact=dic[1],
                            user__exact=user.pk)
                        if item.count != value:
                            item.count = value
                            item.save()
                    except ClassificationCount.DoesNotExist:
                        form = ClassificationCountForm(data)
                        if form.is_valid():
                            form.save()
                    except ClassificationCount.MultipleObjectsReturned:
                        #print('ERROR')
                        pass
                current = log.time.date()
            key = log.classification + ':' + log.protected_type
            #This needs to be handled by minus iterator to track previous classification
            if log.flag == 0:
                pass                
            elif log.flag > 0:
                #If modifying or creating increment count of current classification
                mapping[key] = mapping[key] + 1 if key in mapping else 1

        for key in mapping:
            try:
                mapping[key] = mapping[key] - minus[date][key]
            except KeyError:
                pass
                #Just means no modifications or deletions for that key on that date

        for key, value in mapping.items():
            dic = key.split(':')
            if dic[1]:
                protected_type = dic[1]
            else:
                protected_type = ''
            data = {
                'classification': dic[0], 
                'protected_type': protected_type, 
                'count': value, 
                'date': current, 
                'user': user.pk}
            try:
                item = ClassificationCount.objects.get(
                    date__exact=current,
                    classification__exact=dic[0],
                    protected_type__exact=dic[1],
                    user__exact=user.pk)
                if item.count != value:
                    item.count = value
                    item.save()
            except ClassificationCount.DoesNotExist:
                form = ClassificationCountForm(data)
                if form.is_valid():
                    form.save()
            except ClassificationCount.MultipleObjectsReturned:
                #print('ERROR')
                pass

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
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    reader = csv.DictReader(fs.open(filename, 'r'))
    if set(['Datasource Description', 'Schema', 'Table Name', 'Column Name', 'Classification Name']).issubset(reader.fieldnames):    
        for row in reader:
            data_list = re.split(':', row['Datasource Description'])
            if len(data_list) > 3:
                database = data_list[3].strip()
            else:
                database = row['Datasource Description'].strip()
            try: 
                obj = Classification.objects.get(
                        datasource__exact=database,
                        schema__exact=row['Schema'],
                        table__exact=row['Table Name'],
                        column__exact=row['Column Name'])

                data = {}

                mapping = {
                    'Protected Type': 'protected_type',
                    }
                for key, value in mapping.items():
                    if key in reader.fieldnames:
                        data[value] = row[key]

                if 'Application' in reader.fieldnames:
                    try:
                        data['owner'] = Application.objects.get(acronym__exact=row['Application']).pk
                    except Application.DoesNotExist:
                        data['owner'] = Application.objects.create(name=row['Application'], acronym=row['Application']).pk
                

                classy = row['Classification Name']
                classy = classy.lower()
                classy = re.sub(' ', '_', classy)
                classy = translate[classy]


                if classy in poptions:
                    data['classification'] = 'PE'
                    data['protected_type'] = classy
                else:
                    data['classification'] = classy 

                form = ClassificationForm(data, instance=obj)

                if form.is_valid() and form.has_changed():
                    tmp = form.save(user, None)
                    if 'Dependencies' in reader.fieldnames:
                        if row['Dependencies'] != '':
                            depens = row['Dependencies'].split(',')
                            for dep in depens:
                                try:
                                    app = Application.objects.get(acronym__exact=dep)
                                    tmp.dependents.add(app)
                                except Application.DoesNotExist:
                                    app = Application.objects.create(name=dep, acronym=dep)
                                    tmp.dependents.add(app)
                
            except MultipleObjectsReturned:
                # error
                #print('error')
                pass

            except ObjectDoesNotExist:
                data = {}
                if 'notes' in reader.fieldnames:
                    data['notes'] = row['notes'][:400]
                if 'masking instructions' in reader.fieldnames:
                    data['masking'] = row['masking instructions'][:200]
                if 'Protected Type' in reader.fieldnames:
                    proty = row['Protected Type']
                    proty = proty.lower()
                    proty = re.sub(' ', '_', proty)
                    proty = translate[proty]
                    data['protected_type'] = proty
                if 'Application' in reader.fieldnames:
                    if row['Application'] != '':
                        try:
                            data['owner'] = Application.objects.get(acronym__exact=row['Application']).pk
                        except Application.DoesNotExist:
                            data['owner'] = Application.objects.create(name=row['Application'], acronym=row['Application']).pk

                classy = row['Classification Name']
                classy = classy.lower()
                classy = re.sub(' ', '_', classy)
                classy = translate[classy]

                if classy in poptions:
                    data['classification'] = 'PE'
                    data['protected_type'] = classy
                else:
                    data['classification'] = classy

                data['datasource'] = database
                data['schema'] = row['Schema']
                data['table'] =  row['Table Name']
                data['column'] = row['Column Name']
                data['creator'] = user
                data['state'] = 'A'
                form = ClassificationForm(data)
                if form.is_valid():
                    tmp = form.save(user)
                    if 'Dependencies' in reader.fieldnames:
                        if row['Dependencies'] != '':
                            depens = row['Dependencies'].split(',')
                            for dep in depens:
                                try:
                                    app = Application.objects.get(acronym__exact=dep)
                                    tmp.dependents.add(app)
                                except Application.DoesNotExist:
                                    app = Application.objects.create(name=dep, acronym=dep)
                                    tmp.dependents.add(app)
    #consider keeping the files? Allowing security audit, although data duplication
    fs.delete(filename)

@background(queue='upload')
def upload(filename, user):
    process_file(filename, user)
        
