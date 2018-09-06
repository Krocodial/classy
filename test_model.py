from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.contrib.auth.models import User
from classy.models import *

choices = ['unclassified', 'public', 'confidential', 'protected_a', 'protected_b', 'protected_c']

class existanceTests(TestCase):

    def setUp(self):
        user = User.objects.create_superuser('super', 'xx@xx.com', 'super_password')
        user.save()


        for choice in choices:
            classification.objects.create(
                classification_name=choice, 
                datasource_description='test_ds',
                schema='test_schema', 
                table_name='test_table',
                column_name='test_column',
                created_by='testo',
                state='Active'
                )

    def test_invalid(self):
        tmp = classification.objects.create(
            classification_name='invalid'
        )
	    #self.assertEqual(tmp.pk, None)

        tmp = classification.objects.create()



    def test_basic_creation(self):
        #lion = classification.objects.get(name='lion')
        #self.assertEqual(lion.speak(), 'the lion')
        pass


    def test_modi(self):
        c = Client()
        response = c.post(reverse('classy:index'), {'username': 'super', 'password': 'super_password'})

        
