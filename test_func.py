from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.contrib.auth.models import User
import tempfile

from classy.forms import *
from classy.models import *

class postTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='basic', is_staff=False)
        user.set_password('password')
        user.save()
        user = User.objects.create(username='staff', is_staff=True)
        user.set_password('staff_password')
        user.save()

        self.client = Client()
        response = self.client.post(reverse('classy:index'), {'username': 'staff', 'password': 'staff_password'})

    def test_uploader(self):
        c = self.client

        #Needs some troubleshooting
        '''
        with tempfile.NamedTemporaryFile(suffix='.csv') as fp:
            response = c.post(reverse('classy:uploader'), {'name': fp.name, 'attachment': fp})
            self.assertEqual(response.status_code, 200)
        '''
        data = {'not_file': 'hehe.he'}
        response = c.post(reverse('classy:uploader'), data)
        self.assertEqual(response.status_code, 422)

    def test_download(self):
        c = self.client

        
