from django.test import TestCase
from django.db.utils import *

from classy.models import Classification, ClassificationCount, ClassificationLogs, ClassificationReview, ClassificationReviewGroups
from classy.forms import *

import datetime

choices = ['UN', 'PU', 'PE', 'CO']
#Define what can be protected and what cannot for testing
prot_choices = ['PE', 'CO']

#Public and Unclassified require empty string val
protected = ['PA', 'PB', 'PC', '']
states = ['A', 'I', 'P']


class existanceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('super', 'xx@xx.com', 'super_password')
        #self.user.save()


        self.data = {
            'datasource': 'testo',
            'schema': 'testo',
            'table': 'testo',
            'column': 'testo',
            'creator': self.user.id,
            'state': 'A',
            'classification': 'PU',
            'masking': '',
            'notes': ''
        }        

    def test_invalid_classifications(self):
        data = self.data

        invalid_vals = ['', 'protected_a', 'PROT A', 'sd320', "'; DROP TABLE Classifications;--", '...', '023)(_+']
        
        for val in invalid_vals:
            data['classification'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), False)
            
    def test_valid_classifications(self):
        data = self.data

        for val in choices:
            data['classification'] = val
            table_val = data['table'] + 'a'
            data['table'] = table_val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), True)
            tmp = form.save(self.user.pk, self.user.pk)
            new = Classification.objects.get(classification__exact=val,table__exact=table_val)
            self.assertEqual(tmp.pk, new.pk)

    def test_invalid_protected(self):
        data = self.data
        
        invalid_vals = ['protected_a', 'PROT A', 'sd320', "'; DROP TABLE Classifications;--", '...', '023)(_+', 'CO']
        for clas in choices:
            data['classification'] = clas
            for val in invalid_vals:
                data['protected_type'] = val
                form = ClassificationForm(data)
                self.assertEqual(form.is_valid(), False)
            
    def test_valid_protected(self):
        data = self.data

        for clas in choices:
            data['classification'] = clas
            for val in protected:
                data['protected_type'] = val
                data['table'] = data['table'] + 'a'
                form = ClassificationForm(data)
                self.assertEqual(form.is_valid(), True)
                tmp = form.save(self.user.pk, self.user.pk)
                new = Classification.objects.get(pk=tmp.pk)
                if tmp.classification in ['UN', 'PU']:
                    self.assertEqual('', tmp.protected_type)

    def test_invalid_states(self):
        data = self.data

        invalid_states = ['', 'procte', '12093', ';;]293#@$%', 'active', 'pending', 'deleted', 'CO']

        for val in invalid_states:
            data['state'] = val
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), False)

    def test_valid_states(self):
        data = self.data
        data['classification'] = 'PU'
        for val in states:
            data['state'] = val
            data['table'] = data['table'] + 'b'
            form = ClassificationForm(data)
            self.assertEqual(form.is_valid(), True)
            tmp = form.save(self.user.pk, self.user.pk)
            new = Classification.objects.get(pk=tmp.pk)
            self.assertIsNotNone(new)

    def test_missing_classification_vals(self):
        for key in ['classification', 'datasource', 'schema', 'table', 'column', 'creator', 'state']:
            classy = dict(self.data)
            classy[key] = ''
            form = ClassificationForm(classy)
            self.assertEqual(form.is_valid(), False)
        for key in ['masking', 'notes']:
            classy = dict(self.data)
            classy[key] = ''
            form = ClassificationForm(classy)
            self.assertEqual(form.is_valid(), True)

class creationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='basic', is_staff=False)
        self.user.set_password('password')
        self.user.save()
        data = {'classification': 'PU', 'schema': 'testo', 'table': 'testo', 'column': 'testo', 'datasource': 'testo', 'creator': self.user.id, 'state': 'A', 'masking': 'delet the data', 'notes': 'this data contains a little bit of PII'}
        form = ClassificationForm(data)
        tmp = form.save(self.user.pk, self.user.pk)
        self.classy = tmp.pk#Classification.objects.get(pk=tmp.pk)
    
        data = {'user': self.user.id}
        form = ClassificationReviewGroupForm(data)
        tmp = form.save()
        self.group = tmp.pk
        new = ClassificationReviewGroups.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)


    def test_classification_count(self):
        data = {'classification': 'PU', 'count': 99, 'date': datetime.datetime.now().date(), 'user': self.user.id}
        form = ClassificationCountForm(data)
        tmp = form.save()
        new = ClassificationCount.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_classification_exception(self):
        pass

    '''
    def test_classification_log(self):
        data = {'classy': self.classy, 'flag': 2, 'new_Classification': 'PU', 'old_Classification': 'CO', 'user': self.user.id, 'state': 'A', 'approver': self.user.id}
        form = ClassificationLogForm(data)
        tmp = form.save()
        new = ClassificationLogs.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_classification_review(self):
        data = {'classy': self.classy, 'group': self.group, 'classification': 'PU', 'flag': 1}
        form = ClassificationReviewForm(data)
        if form.is_valid():
            tmp = form.save()
        else:
            print(form.errors)
        new = ClassificationReview.objects.get(pk=tmp.pk)
        self.assertIsNotNone(new)

    def test_deletion_protection(self):
        data = {'classy': self.classy, 'flag': 2, 'classification': 'PU', 'user': self.user.id, 'state': 'A', 'approver': self.user.id}
        form = ClassificationLogForm(data)
        tmp = form.save()
    
        with self.assertRaises(IntegrityError):
            Classification.objects.get(pk=self.classy).delete() 

        try:
            tmp.delete()
            Classification.objects.get(pk=self.classy).delete()
        except IntegrityError:
            self.fail("test_deletion_protection raised IntegrityError")
    '''     





        
