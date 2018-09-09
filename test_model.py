from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.contrib.auth.models import User
from classy.models import *
from classy.forms import ClassificationForm

choices = ['CONFIDENTIAL', 'PUBLIC', 'Unclassified', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']
states = ['Active', 'Inactive', 'Pending']


class existanceTests(TestCase):

    def setUp(self):
        user = User.objects.create_superuser('super', 'xx@xx.com', 'super_password')
        user.save()

        self.data = {
            'datasource_description': 'testo',
            'schema': 'testo',
            'table_name': 'testo',
            'column_name': 'testo',
            'created_by': 'test',
            'state': 'Active',
            'classification_name': 'public'
        }        

    def test_invalid_classifications(self):
        data = self.data

        invalid_vals = ['', 'protected_a', 'PROT A', 'sd320', "'; DROP TABLE classifications;--", '...', '023)(_+']
        
        for val in invalid_vals:
            data['classification_name'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), False)
            
    def test_valid_classifications(self):
        data = self.data

        for val in choices:
            data['classification_name'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), True)
            tmp = form.save()
            new = classification.objects.get(classification_name=val)
            self.assertEqual(tmp.pk, new.pk)

    def test_invalid_states(self):
        data = self.data

        invalid_states = ['', 'procte', '12093', ';;]293#@$%', 'active', 'pending', 'deleted']

        for val in invalid_states:
            data['state'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), False)

    def test_valid_states(self):
        data = self.data
        data['classification_name'] = 'PUBLIC'
        for val in states:
            data['state'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), True)
            tmp = form.save()
            new = classification.objects.get(pk=tmp.pk)
            self.assertIsNotNone(new)

    def test_missing_classification_vals(self):
        for key in self.data:
            data = self.data
            data[key] = ''
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), False)


class deletionTests(TestCase):
    def setUp(self):
        data = {'classification_name': 'PUBLIC', 'datasource_description': 'testo', 'schema': 'testo', 'table_name': 'testo', 'column_name': 'testo', 'created_by': 'admin', 'state': 'Active'}
        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        tmp = form.save()
        data = {'classy': tmp, 'action_flag': 0, 'n_classification': 'PUBLIC', 'o_classification': 'CONFIDENTIAL', 'user_id': 0, 'state': 'Active', 'approved_by': 'admin'}
            





        
