from django.test import TestCase, Client
from .models import classification
from django.contrib.auth.models import User
from .forms import advancedSearch, UploadFileForm, loginform
# Create your tests here.
class searchFormTestCase(TestCase):

	def __init__(self, *args, **kwargs):
		super(searchFormTestCase, self).__init__(*args, **kwargs)
		self.client = Client()

	def setUp(self):
		classification.objects.create(classification_name = 'PUBLIC', schema='test', table_name='testtable', column_name='test_column', datasource_description='thisistehadatadkfj', state='Active')
		user = User.objects.create(username='testuser', is_staff=True)
		user.set_password('12345')
		user.save()
		
		#self.c = Client()
		response = self.client.post('/', {'username': 'testuser', 'password': '12345'})

		response = self.client.get('/data')
		self.assertEqual(response.status_code, 200)


	def test_empty_get(self):
		c = self.client
		response = c.get('/data')
		self.assertEqual(response.status_code, 200)
		response = c.get('/home')
		self.assertEqual(response.status_code, 200)
		response = c.get('/search')
		self.assertEqual(response.status_code, 200)
		response = c.get('/uploader')
		self.assertEqual(response.status_code, 200)	
	def test_login_form(self):
		form_data = {'username': 'example_user_name12389(0*&$%_*', 'password': 'Passwordoftheuser231948(*$U"'}
		form = loginform(data=form_data)
		self.assertTrue(form.is_valid())
	def test_search_form(self):
		form_data = {}
