from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
#from django.contrib.auth.models import User
from django.db.utils import *

from classy.models import *
from classy.forms import *


choices = ['CO', 'PU', 'UN', 'PA', 'PB', 'PC']
states = ['A', 'I', 'P']


class existanceTests(TestCase):

    def setUp(self):
        user = User.objects.create_superuser('super', 'xx@xx.com', 'super_password')
        user.save()

        self.data = {
            'datasource': 'testo',
            'schema': 'testo',
            'table': 'testo',
            'column': 'testo',
            'creator': user.id,
            'state': 'A',
            'classification_name': 'PU',
            'masking': '',
            'notes': ''
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
            new = classification.objects.get(classification_name=val,column='testo')
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
        data['classification_name'] = 'PU'
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

class creationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='basic', is_staff=False)
        self.user.set_password('password')
        self.user.save()
        data = {'classification_name': 'PU', 'schema': 'testo', 'table': 'testo', 'column': 'testo', 'datasource': 'testo', 'creator': self.user.id, 'state': 'A', 'masking': 'delet the data', 'notes': 'this data contains a little bit of PII'}
        form = ClassificationForm(data)
        tmp = form.save()
        self.classy = tmp.pk#classification.objects.get(pk=tmp.pk)
    
        data = {'user': self.user.id}
        form = classificationReviewGroupForm(data)
        tmp = form.save()
        self.group = tmp.pk
        new = classification_review_groups.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)


    def test_classification_count(self):
        data = {'classification_name': 'PU', 'count': 99, 'date': datetime.datetime.now().date(), 'user': self.user.id}
        form = classificationCountForm(data)
        tmp = form.save()
        new = classification_count.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_classification_exception(self):
        data = {'classy': self.classy}
        form = classificationExceptionForm(data)
        tmp = form.save()
        new = classification_exception.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_classification_log(self):
        data = {'classy': self.classy, 'flag': 2, 'new_classification': 'PU', 'old_classification': 'CO', 'user': self.user.id, 'state': 'A', 'approver': self.user.id}
        form = classificationLogForm(data)
        tmp = form.save()
        new = classification_logs.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_classification_review(self):
        data = {'classy': self.classy, 'group': self.group, 'classification_name': 'PU', 'flag': 1}
        form = classificationReviewForm(data)
        if form.is_valid():
            tmp = form.save()
        else:
            print(form.errors)
        new = classification_review.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_deletion_protection(self):
        data = {'classy': self.classy, 'flag': 2, 'new_classification': 'PU', 'old_classification': 'CO', 'user': self.user.id, 'state': 'A', 'approver': self.user.id}
        form = classificationLogForm(data)
        tmp = form.save()
    
        with self.assertRaises(IntegrityError):
            classification.objects.get(pk=self.classy).delete() 

        tmp.delete()
        classification.objects.get(pk=self.classy).delete()

            





        
