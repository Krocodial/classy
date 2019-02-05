from django.test import TestCase
from django.contrib.auth.models import User

from classy.models import data_authorization, dataset_authorization, classification
from classy.helper import query_constructor
from classy.forms import ClassificationForm

class authTests(TestCase):
    def setUp(self):
	

	
        user = User.objects.create(username='no_access', is_staff=False)
        user.set_password('password')
        user.save()

        self.no = user

        user = User.objects.create(username='full_access', is_staff=False)
        user.set_password('password')
        user.save()

        self.full = user

        user = User.objects.create(username='group_full_access', is_staff=False)
        user.set_password('password')
        user.save()

        self.group_full = user

        user = User.objects.create(username='group_no_access', is_staff=False)
        user.set_password('password')
        user.save()

        self.group_no = user

        data = {
            'datasource': 'testo',
            'schema': 'testo',
            'table': 'testo',
            'column': 'testo',
            'creator': user.id,
            'state': 'A',
            'classification_name': 'PU'
        }

        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        form.save()
		
        data['table'] = 'UWU'
        form = ClassificationForm(data)
        self.assertEqual(form.is_valid(), True)
        form.save()
		
        d1 = data_authorization.objects.create(
            name="All",
        )

        self.full.profile.data_authorizations.add(d1)
        self.full.save()
	
        ds = dataset_authorization(name='full')
        ds.save()
        ds.data_authorizations.add(d1)
        ds.save()

        self.group_full.profile.dataset_authorizations.add(ds)
        self.group_full.save()

        ds1 = dataset_authorization(name='empty')
        ds1.save()

        self.group_no.profile.dataset_authorizations.add(ds1)
        self.group_no.save()

    def test_unauth(self):
        count = classification.objects.all().count()
        self.assertEqual(2, count)
        count = query_constructor(classification.objects.all(), self.no).count()
        self.assertEqual(0, count)

    def test_auth(self):
        count = classification.objects.all().count()
        self.assertEqual(2, count)
        count = query_constructor(classification.objects.all(), self.full).count()
        self.assertEqual(2, count)

    def test_group_unauth(self):
        count = classification.objects.all().count()
        self.assertEqual(2, count)
        count = query_constructor(classification.objects.all(), self.group_no).count()
        self.assertEqual(0, count)

    def test_group_auth(self):
        count = classification.objects.all().count()
        self.assertEqual(2, count)
        count = query_constructor(classification.objects.all(), self.group_full).count()
        self.assertEqual(2, count)



