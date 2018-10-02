from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.template.loader import render_to_string

import tempfile, json

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

    
    def test_review_process(self):
        
        data = {
            'datasource_description': 'testo',
            'schema': 'testo',
            'table_name': 'testo',
            'column_name': 'testo',
            'created_by': 'test',
            'state': 'Active',
            'classification_name': 'PUBLIC'
        }

        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        tmp = form.save()

        c = Client()
        c.post(reverse('classy:index'), {'username': 'basic', 'password': 'password'})
        response = c.get(reverse('classy:search'), {'query': 'test'})
        self.assertContains(response, '<td>testo</td>')
        toMod = [{'id': tmp.pk, 'classy': 'PROTECTED A'}]
        c.post(reverse('classy:modi'), {'toMod': json.dumps(toMod)})
        
        toDel = [tmp.pk]
        c.post(reverse('classy:modi'), {'toDel': json.dumps(toDel)}) 
    
        c.get(reverse('classy:user_logout'))
        c.post(reverse('classy:index'), {'username': 'staff', 'password': 'staff_password'})
        response = c.get(reverse('classy:review'))
        
        self.assertContains(response, '<small class="text-muted"> basic</small>', 2)

        grps = classification_review_groups.objects.values('id')
        indices = []
        for i in grps:
            indices.append(i['id'])
        testo = classification.objects.get(pk=tmp.pk)
        
        response = c.post(reverse('classy:review'), {'group':indices[0], 'denied': json.dumps([])})
        
        testo.refresh_from_db() 
        self.assertEqual(testo.classification_name, 'PROTECTED A')	 

        c.post(reverse('classy:review'), {'group':indices[1], 'denied': json.dumps([])})
        #Has the value been deleted?
        response = c.get(reverse('classy:search'), {'query': 'test'}) 
        self.assertNotContains(response, '<td>testo</td>')

    def test_basic_search(self):

        data = {
            'datasource_description': 'testo',
            'schema': 'testo',
            'table_name': 'testo',
            'column_name': 'testo',
            'created_by': 'test',
            'state': 'Active',
            'classification_name': 'PUBLIC'
        }

        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        tmp = form.save()

        c = Client()
        response = c.post(reverse('classy:index'), {'username': 'basic', 'password': 'pass'})
        self.assertContains(response, 'Not an authorized user')
        response = c.post(reverse('classy:index'), {'username': 'basic', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:home'))
        self.assertContains(response, 'Welcome ')

        response = c.get(reverse('classy:data'))
        self.assertNotContains(response, '<td>testo</td>')

        response = c.get(reverse('classy:search'), {'query': 'test'})
        self.assertContains(response, '<td>testo</td>')

        response = c.get(reverse('classy:search'), {'query': 'password'})
        self.assertNotContains(response, '<td>testo</td>') 

        toDel = [tmp.pk]
        response = c.post(reverse('classy:modi'), {'toDel': json.dumps(toDel)})
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('classy:search'), {'query': 'test'})
        self.assertContains(response, '<td>testo</td>')
        
        toMod = [{'id': tmp.pk, 'classy': 'PROTECTED A'}]
        response = c.post(reverse('classy:modi'), {'toMod': json.dumps(toMod)})
        self.assertEqual(response.status_code, 200)

    def test_staff_search(self):
        data = {
            'datasource_description': 'testo',
            'schema': 'testo',
            'table_name': 'testo',
            'column_name': 'testo',
            'created_by': 'test',
            'state': 'Active',
            'classification_name': 'PUBLIC'
        }

        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        tmp = form.save()

        c = Client()
        response = c.post(reverse('classy:index'), {'username': 'staff', 'password': 'pass'})
        self.assertContains(response, 'Not an authorized user')
        response = c.post(reverse('classy:index'), {'username': 'staff', 'password': 'staff_password'})
        self.assertEqual(response.status_code, 302)
        response = c.get(reverse('classy:home'))
        self.assertContains(response, 'Welcome ')

        response = c.get(reverse('classy:data'))
        self.assertNotContains(response, '<td>testo</td>')

        response = c.get(reverse('classy:search'), {'query': 'test'})
        self.assertContains(response, '<td>testo</td>')

        response = c.get(reverse('classy:search'), {'query': 'password'})
        self.assertNotContains(response, '<td>testo</td>')

        toDel = [tmp.pk]
        response = c.post(reverse('classy:modi'), {'toDel': json.dumps(toDel)})
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('classy:search'), {'query': 'test'})
        self.assertNotContains(response, '<td>testo</td>')

        toMod = [{'id': tmp.pk, 'classy': 'PROTECTED A'}]
        response = c.post(reverse('classy:modi'), {'toMod': json.dumps(toMod)})
        self.assertEqual(response.status_code, 200)

    def test_uploader(self):
        #c = self.client

        #Needs some troubleshooting
        '''
        with tempfile.NamedTemporaryFile(suffix='.csv') as fp:
            response = c.post(reverse('classy:uploader'), {'name': fp.name, 'attachment': fp})
            self.assertEqual(response.status_code, 200)
        '''
        #data = {'not_file': 'hehe.he'}
        #response = c.post(reverse('classy:uploader'), data)
        #self.assertEqual(response.status_code, 422)

    def test_download(self):
        c = self.client

        
