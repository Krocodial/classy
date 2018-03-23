import io
import csv
from django.core import files
from .models import classification, classification_logs
from .forms import ClassificationForm
import re
import multiprocessing, time, signal
import threading
import queue

#File for generic scripts
class parent:
	def __init__(self, iden):
		children = []
		self.iden = iden 


def create_thread(inp, lock, th, threads, user):
	print("pending")
	lock.acquire()
	if(inp.closed):
		print('closing')
		threads.remove(th)
		lock.release()
		return
	th.state = 'active'
	print('executing')
	
	try:
		inp.seek(0)
		reader = csv.DictReader(io.StringIO(inp.read().decode()))
	#reader = csv.DictReader(inp.read().decode())
	#print(list(reader.keys()))
		q = re.compile(':')
	#lock.acquire()
	#th.state = 'active'
	#print('executing')
		for row in reader:
			data_list = re.split(':', row['Datasource Description'])
#		print(data_list)
			if not classification.objects.filter(
			schema__exact=row['Schema'], 
			table_name__exact=row['Table Name'], 
			column_name__exact=row['Column Name'], 
			datasource_description=data_list[3]):
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
						log = classification_logs(classy_id = tmp.id, action_flag=2, n_classification=row['Classification Name'], o_classification=row['Classification Name'], user_id = user, state='Active')
						log.save()
					else:
						print(form.errors)
				except Exception as e:
					print(e)
					pass
		print('finished')
		inp.close()
		threads.remove(th)
		lock.release()
	except Exception as e:
		print(e)
		pass


def demo():
	sql = classification(
	classification_name=row['Classification Name'], 
	schema=row['Schema'], 
	table_name=row['Table Name'], 
	column_name=row['Column Name'], 
	category=row['Category'], 
	datasource_description=data_list[3],
	created_by = user,
	state='Active')
	sql.save()

	log = classification_logs(classy_id = sql.id, action_flag=2, n_classification=row['Classification Name'], o_classification=row['Classification Name'], user_id = user, state='Active')
	log.save()

		
		#log = classification_logs(classy_id = , action_flag=2, n_classification=row['Classification Name'], o_classification=row['Classification Name'], user_id = user)
		#log.save()

	inp.close()
	threads.remove(th)
	lock.release()
			#print('tuple inserted')
		
		#print(row['Classification Name'])
		
	#	print(row['Classification Name'])	
#function to be called by view.uploader


def example(lock):
	lock.acquire()
	print('executing')
	time.sleep(10)
	lock.release()

	
	

	

	

	
	
