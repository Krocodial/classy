from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from classy.models import classification_review_groups, classification, classification_review, data_authorization
from classy.views import home, login_complete, download, review, exceptions, log_list, log_detail, modi, search, uploader

import json

class renderTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.basic = User.objects.create(username='basic', password='password', is_staff=False)
        self.staff = User.objects.create(username='staff', password='password', is_staff=True)
        self.supa = User.objects.create_superuser('super', 'xx@xx.com', 'password')
        self.anon = AnonymousUser()
        self.users = [self.anon, self.basic, self.staff, self.supa]
    '''
    def test_index_view(self):
        index_request = self.factory.get(reverse('classy:index'))
        users = [self.anon, self.basic, self.staff, self.supa]
        tran = {self.anon: 'anon', self.basic: 'basic', self.staff: 'staff', self.supa: 'supa'}
        pages = {'anon': settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete'), scope='username email', state='alskdfjl;isiejf'), 'basic': reverse('classy:home'), 'staff': reverse('classy:home'), 'supa': reverse('classy:home')}

        for user in users:
            request = index_request
            request.user = user
            response = index(request)
            response.client = Client()
            self.assertRedirects(response, pages[tran[user]], fetch_redirect_response=False)
    '''

    def test_login_complete_view(self):
        for user in self.users:
            request = self.factory.get(reverse('classy:login_complete'))
            request.user = user
            response = login_complete(request)
            self.assertEquals(response.status_code, 403)

    def test_home_view(self):
        response_codes = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        for user in self.users:
            request = self.factory.get(reverse('classy:home'))
            request.user = user
            response = home(request)
            self.assertEquals(response.status_code, response_codes[user])

    def test_download_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 302, self.supa: 302}
        response_codes_post = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}

        for user in self.users:
            request = self.factory.get(reverse('classy:download'))
            request.user = user
            response = download(request)
            self.assertEquals(response.status_code, response_codes_get[user])
            request = self.factory.post(reverse('classy:download'))
            request.user = user
            response = download(request)
            self.assertEquals(response.status_code, response_codes_post[user])

    def test_review_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        response_codes_post_invalid = {self.anon: 302, self.basic: 302, self.staff: 400, self.supa: 400}
        response_codes_post_valid = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa:200}
        for i in range(1,5):
            print(i)
            rev = classification_review.objects.create(
                    classy=classification.objects.create(
                        classification_name='PA',
                        datasource='UWU',
                        schema='owo',
                        table='uwu',
                        column='testo',
                        creator=self.basic,
                        state='A'
                        ),
                    group = classification_review_groups.objects.create(user=self.basic),
                    classification_name = 'PU',
                    flag = 0)
        group = 1
        print(classification_review_groups.objects.all())
        for user in self.users:
            request = self.factory.get(reverse('classy:review'))
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_get[user])

            request = self.factory.post(reverse('classy:review'))
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_post_invalid[user])

            request = self.factory.post(reverse('classy:review'), data={'group': group})
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_post_valid[user])

            group = group + 1

    def test_exceptions_view(self):
        response_codes = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        for user in self.users:
            request = self.factory.get(reverse('classy:exceptions'))
            request.user = user
            response = exceptions(request)
            self.assertEquals(response.status_code, response_codes[user])

            request = self.factory.post(reverse('classy:exceptions'), data={'query': 'password'})
            request.user = user
            response = exceptions(request)
            self.assertEquals(response.status_code, response_codes[user])

    def test_log_list_view(self):
        response_codes = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        for user in self.users:
            request = self.factory.get(reverse('classy:log_list'))
            request.user = user
            response = log_list(request)
            self.assertEquals(response.status_code, response_codes[user])

            request = self.factory.post(reverse('classy:log_list'), data={'query': 'password'})
            request.user = user
            response = log_list(request)
            self.assertEquals(response.status_code, response_codes[user])
    
    def test_log_detail_view(self):
        response_codes = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        rev = classification.objects.create(
            classification_name='PA',
            datasource='Avengers',
            schema='endgame',
            table='hype',
            column='yeet',
            creator=self.basic,
            state='A'
            )
        d1 = data_authorization.objects.create(
                name='All',
            )
        for user in self.users:
            request = self.factory.get(reverse('classy:log_detail', args=[rev.pk]))
            request.user = user
            response = log_detail(request, rev.pk)
            self.assertEquals(response.status_code, 302)

            if user == self.anon:
                continue

            user.profile.data_authorizations.add(d1)
            user.profile.save()

            request = self.factory.get(reverse('classy:log_detail', args=[rev.pk]))
            request.user = user
            response = log_detail(request, rev.pk)
            self.assertEquals(response.status_code, response_codes[user])

    def test_modi_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 302, self.supa: 302}
        response_codes_post = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}

        for user in self.users:
            rev = classification.objects.create (
                    classification_name='CO',
                    datasource='game',
                    schema='of',
                    table='thrones',
                    column='hype',
                    creator=self.basic,
                    state='A'
                    )

            toMod = json.dumps([{"id": rev.pk, "classy": "PUBLIC"}])
            toDel = json.dumps([rev.pk])
            modData = {"toMod": toMod}
            delData = {"toDel": toDel}
        
            request = self.factory.get(reverse('classy:modi'))
            request.user = user
            response = modi(request)
            self.assertEquals(response.status_code, response_codes_get[user]) 

            request = self.factory.post(reverse('classy:modi'), data={'toMod': toMod})
            request.user = user
            response = modi(request)
            self.assertEquals(response.status_code, response_codes_post[user])

            rev.refresh_from_db()
            if user.is_staff:
                self.assertEquals(rev.classification_name, 'PU')
                self.assertEquals(rev.state, 'A')
            elif user.is_authenticated:
                self.assertEquals(rev.state, 'P')
            else:
                self.assertEquals(rev.state, 'A')

            request = self.factory.post(reverse('classy:modi'), data={'toDel': toDel})
            request.user = user
            response = modi(request)
            self.assertEquals(response.status_code, response_codes_post[user])

            if user.is_staff:
                rev.refresh_from_db()
                self.assertEquals(rev.state, 'I')
            elif user.is_authenticated:
                self.assertEquals(rev.state, 'P')
            else:
                self.assertEquals(rev.state, 'A')

    def test_search_view(self):
        response_codes_get = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        for user in self.users:
            request = self.factory.get(reverse('classy:search'))
            request.user = user
            response = search(request)
            self.assertEquals(response.status_code, response_codes_get[user])

    def test_uploader_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        for user in self.users:
            request = self.factory.get(reverse('classy:uploader'))
            request.user = user
            response = uploader(request)
            self.assertEquals(response.status_code, response_codes_get[user])

