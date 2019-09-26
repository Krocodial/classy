from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.forms.models import model_to_dict

from classy.models import Application, ClassificationReviewGroups, Classification, ClassificationReview, DataAuthorization
from classy.views import index, home, login_complete, download, review, exceptions, log_list, log_detail, modi, search, uploader
from classy.forms import ClassificationForm, AdvancedSearch, BasicSearch

import json, os, factory

from classy.models import classification_choices, protected_series, state_choices

from .factories import DataAuthFactory, OwnerFactory, UserFactory, ClassyFactory

choices = ['Public', 'Confidential', 'Personal', 'Unclassified']
protected = ['Protected A', 'Protected B', 'Protected C', '']
prot_choices = ['Personal', 'Confidential']

#Since logon is forced in tests disable expiry/invalid token middleware.
@override_settings(MIDDLEWARE = [mc for mc in settings.MIDDLEWARE if mc != 'classy.middleware.authentication.authentication_middleware'])
class renderTest(TestCase):
    #Create fake data, users, and associated permissions for testing. 
    @classmethod
    def setUpClass(cls):
        users = ['basic', 'staff', 'superuser']
        acces = {'full': '', 'partial': 'db01', 'none': 'nonexistantdatasource'}
        options = ['db01', 'db02', '']

        for key, value in acces.items():
            d1 = DataAuthFactory(name=key, datasource=value)
            for username in users:
                supa = False
                staff = False
                if username == 'superuser':
                    supa = True    
                    staff = True
                if username == 'staff':
                    staff = True
            
                user = UserFactory(username = username + '-' + key, email= username + '-' + key + '@bcgov.ca', is_staff=staff, is_superuser=supa)
                user.profile.data_authorizations.add(d1)
                user.save()

        OwnerFactory.create_batch(10)

        for ds in options:
            for sc in options:
                for ta in options:
                    for co in options:
                        ClassyFactory(datasource=ds, schema=sc, table=ta, column=co)

        ClassyFactory.create_batch(200)
        super(renderTest, cls).setUpClass()

    def setUp(self):
        self.options = ['db01', 'db02', '']

    def test_index_view(self):

        for user in User.objects.all():
            c = Client()

            response = c.get(reverse('classy:index'))
            self.assertRedirects(response, settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete')), status_code=302, target_status_code=200, fetch_redirect_response=False)

            c.force_login(user)

            response = c.get(reverse('classy:index'))
            self.assertRedirects(response, reverse('classy:home'))
        

    def test_login_complete_view(self):
        for user in User.objects.all():
            c = Client()
            c.force_login(user)        
    
            response = c.get(reverse('classy:login_complete'))
            self.assertEquals(response.status_code, 403)
        
        c = Client() 
        response = c.get(reverse('classy:login_complete'))
        self.assertEquals(response.status_code, 403)

    def test_home_view(self):
        for user in User.objects.all():
            c = Client()
            
            response = c.get(reverse('classy:home'))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:index') + '?next=' + reverse('classy:home')
            self.assertRedirects(response, url, fetch_redirect_response=False)

            c.force_login(user)
            response = c.get(reverse('classy:home'))
            self.assertEquals(response.status_code, 200)

    def test_download_view(self):
        options = ['datasource', 'schema', 'table', 'column']
        for user in User.objects.all():
            c = Client()
            
            
            response = c.get(reverse('classy:download'))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:index') + '?next=' + reverse('classy:download')
            self.assertRedirects(response, url, fetch_redirect_response=False)

            c.force_login(user)
            response = c.get(reverse('classy:download'))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:home')
            self.assertRedirects(response, url)

            for op in ['db01', 'db02']:
                data = {key: str(op) for key in options}
                #data =  {'datasource': op, 'schema': op, 'table': op, 'column': op}
                response = c.post(reverse('classy:download'), data=data)
                #print(Classification.objects.filter(datasource=op, schema=op, table=op))
                #print(response.content)
                self.assertEquals(response.status_code, 200)
                try:
                    text = "{},{},{},{}".format(op, op, op, op)
                    perm = user.username.split('-')
                    if perm[1] == 'full':
                        self.assertContains(response, text)
                    elif perm[1] == 'partial':
                        if op == 'db01':
                            self.assertContains(response, text)
                        else:
                            self.assertNotContains(response, text)
                    elif perm[1] == 'none':
                        self.assertNotContains(response, text)
                except:
                    print(response.content)
                    print(model_to_dict(Classification.objects.get(datasource='db01', schema='db01', table='db01', column='db01')))
                    self.assertEquals(200, 201)

    '''
    def test_review_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        response_codes_post_invalid = {self.anon: 302, self.basic: 302, self.staff: 400, self.supa: 400}
        response_codes_post_valid = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa:200}
        for i in range(1,5):
            rev = ClassificationReview.objects.create(
                    classy=Classification.objects.create(
                        classification='PA',
                        datasource='UWU',
                        schema='owo',
                        table='uwu',
                        column='testo',
                        creator=self.basic,
                        state='A'
                        ),
                    group = ClassificationReviewGroups.objects.create(user=self.basic),
                    classification = 'PU',
                    flag = 0)
        for user, group in zip(self.users, ClassificationReviewGroups.objects.all()):
            request = self.factory.get(reverse('classy:review'))
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_get[user])

            request = self.factory.post(reverse('classy:review'))
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_post_invalid[user])

            request = self.factory.post(reverse('classy:review'), data={'group': group.pk})
            request.user = user
            response = review(request)
            self.assertEquals(response.status_code, response_codes_post_valid[user])

    '''

    def test_exceptions_view(self):
        for user in User.objects.all():
            c = Client()
            
            response = c.get(reverse('classy:exceptions'))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:index') + '?next=' + reverse('classy:exceptions')
            self.assertRedirects(response, url, fetch_redirect_response=False)

            response = c.post(reverse('classy:exceptions'), data={'query': 'db01'})
            self.assertEquals(response.status_code, 302)
            self.assertRedirects(response, url, fetch_redirect_response=False)
    
            c.force_login(user)
            response = c.get(reverse('classy:exceptions'))
            post_response = c.post(reverse('classy:exceptions'), data={'query': 'db01'})
            if user.is_staff:
                self.assertEquals(response.status_code, 200)
                self.assertEquals(post_response.status_code, 200)
            else:
                self.assertEquals(response.status_code, 302)
                self.assertEquals(post_response.status_code, 302)
                url = reverse('classy:index')
                self.assertRedirects(response, url, fetch_redirect_response=False)


    def test_log_list_view(self):
        for user in User.objects.all():
            c = Client()
            
            response = c.get(reverse('classy:log_list'))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:index') + '?next=' + reverse('classy:log_list')
            self.assertRedirects(response, url, fetch_redirect_response=False)

            response = c.post(reverse('classy:log_list'), data={'query': 'db01'})
            self.assertEquals(response.status_code, 302)
            self.assertRedirects(response, url, fetch_redirect_response=False)
    
            c.force_login(user)
            response = c.get(reverse('classy:log_list'))
            post_response = c.post(reverse('classy:log_list'), data={'query': 'db01'})
            self.assertEquals(response.status_code, 200)
            self.assertEquals(post_response.status_code, 200)
   
    def test_log_detail_view(self):
        partial = Classification.objects.get(datasource='db01', schema='db01', table='db01', column='db01')
        full = Classification.objects.get(datasource='db02', schema='db02', table='db02', column='db02')        

        for user in User.objects.all():
            c = Client()
            
            response = c.get(reverse('classy:log_detail', args=[partial.pk]))
            self.assertEquals(response.status_code, 302)
            url = reverse('classy:index') + '?next=' + reverse('classy:log_detail', args=[partial.pk])
            self.assertRedirects(response, url, fetch_redirect_response=False)

            c.force_login(user)
            partial_response = c.get(reverse('classy:log_detail', args=[partial.pk]))
            full_response = c.get(reverse('classy:log_detail', args=[full.pk]))

            partial_html = "<td>{}</td>".format('db01')
            full_html = "<td>{}</td>".format('db02')
            perm = user.username.split('-')
            if perm[1] == 'full':
                self.assertEquals(full_response.status_code, 200)
                self.assertEquals(partial_response.status_code, full_response.status_code)
                self.assertContains(full_response, full_html, count=4, status_code=200)
                self.assertContains(partial_response, partial_html, count=4, status_code=200)
            elif perm[1] == 'partial':
                self.assertEquals(partial_response.status_code, 200)
                self.assertNotEquals(partial_response.status_code, full_response.status_code)
                self.assertContains(partial_response, partial_html, count=4, status_code=200)
            elif perm[1] == 'none':
                self.assertEquals(partial_response.status_code, 302)
                self.assertEquals(partial_response.status_code, full_response.status_code)



    def test_modi_view(self):
        for user in User.objects.all():
            c = Client()
            c.force_login(user)

            rev = ClassyFactory(classification='PU', protected_type='', state='A')
            toMod = json.dumps([{"id": rev.pk, "classy": "Personal", "proty": "Protected B", "own": "---------"}])
            toDel = json.dumps([rev.pk])
            modData = {"toMod": toMod}
            delData = {"toDel": toDel}
 
            response = c.get(reverse('classy:modi'))
            self.assertEquals(response.status_code, 302) 

            response = c.post(reverse('classy:modi'), data={'toMod': toMod})
            self.assertEquals(response.status_code, 200)

            rev.refresh_from_db()
            perm = user.username.split('-')
            if perm[1] == 'full':
                if user.is_staff:
                    self.assertEquals(rev.state, 'A')
                    self.assertEquals(rev.classification, 'PE')
                    self.assertEquals(rev.protected_type, 'PB')
                else:
                    self.assertEquals(rev.state, 'P')
                    self.assertEquals(rev.classification, 'PU')
                    self.assertEquals(rev.protected_type, '')
            else:
                if user.is_staff:
                    self.assertEquals(rev.state, 'A')
                    self.assertEquals(rev.classification, 'PU')
                    self.assertEquals(rev.protected_type, '')
                else:
                    self.assertEquals(rev.state, 'A')
                    self.assertEquals(rev.classification, 'PU')
                    self.assertEquals(rev.protected_type, '')
            
            response = c.post(reverse('classy:modi'), data={'toDel': toDel})
            self.assertEquals(response.status_code, 200)
           
            rev.refresh_from_db()
            perm = user.username.split('-')
            if perm[1] == 'full':
                if user.is_staff:
                    self.assertEquals(rev.state, 'I')
                else:
                    self.assertEquals(rev.state, 'P')
            else:
                if user.is_staff:
                    self.assertEquals(rev.state, 'A')
                else:
                    self.assertEquals(rev.state, 'A')


    def test_search_view(self):
        parameters = ['datasource', 'schema', 'table', 'column', 'classification', 'protected_type', 'state', 'owner']

        for user in User.objects.all():
            c = Client()
            c.force_login(user)
  
            for i in range(50): 
                classy = vars(ClassyFactory.build())
                classy['owner'] = classy['owner_id']
                classy = { key: classy[key] for key in parameters }
                
                response = c.get(reverse('classy:search'), data=classy)
                self.assertEquals(response.status_code, 200)

            for op in ['db01', 'db02']:
                classy = vars(ClassyFactory.build(datasource=op, schema=op, table=op, column=op))
                classy = { key: classy[key] for key in parameters[:4] }    
                response = c.get(reverse('classy:search'), data=classy)   

                html = "<td>{}</td>".format(op)
                perm = user.username.split('-')
                if perm[1] == 'full':
                    self.assertContains(response, html, count=4, status_code=200, html=True)
                elif perm[1] == 'partial':
                    if op == 'db01':
                        self.assertContains(response, html, count=4, status_code=200, html=True)
                    else:
                        self.assertNotContains(response, html, status_code=200, html=True)
                elif perm[1] == 'none':
                    self.assertNotContains(response, html, status_code=200, html=True)

        c = Client()
         
        for i in range(50): 
            classy = vars(ClassyFactory.build())
            classy['owner'] = classy['owner_id']
            classy = { key: classy[key] for key in parameters }
            
            response = c.get(reverse('classy:search'), data=classy)
            self.assertEquals(response.status_code, 302)
        

    '''
    def test_uploader_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        users = self.users
        for user in users:
            request = self.factory.get(reverse('classy:uploader'))
            request.user = user
            response = uploader(request)
            self.assertEquals(response.status_code, response_codes_get[user])
    '''
