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

choices = ['Public', 'Confidential', 'Personal', 'Unclassified']
protected = ['Protected A', 'Protected B', 'Protected C', '']
prot_choices = ['Personal', 'Confidential']

class DataAuthFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DataAuthorization

    name = 'All'
    datasource = ''
    schema = ''
    table = ''
    column = ''

class OwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    acronym = factory.Sequence(lambda n: 'APP' + str(n))
    name = factory.Sequence(lambda n: 'application' + str(n)) 

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user' + str(n))
    email = factory.Sequence(lambda n: 'user' + str(n) + '@email.com')
    is_staff = False
    is_superuser = False


class ClassyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Classification
        django_get_or_create = ('owner',)

    datasource = factory.Faker('sentence', nb_words=4)
    schema = factory.Faker('sentence', nb_words=4)
    table = factory.Faker('sentence', nb_words=4)
    column = factory.Faker('sentence', nb_words=4)

    classification = factory.Faker('random_element', elements=[x[0] for x in classification_choices])
    protected_type = factory.Faker('random_element', elements=[x[0] for x in protected_series])
    state = factory.Faker('random_element', elements=[x[0] for x in state_choices])
 
    creator = factory.Iterator(User.objects.all())
    owner = factory.Iterator(Application.objects.all()) 

    #creator = factory.SubFactory(UserFactory)
    #owner = factory.SubFactory(OwnerFactory)


#Since logon is forced in tests disable expiry/invalid token middleware.
@override_settings(
    MIDDLEWARE = [mc for mc in settings.MIDDLEWARE if mc != 'classy.middleware.authentication.authentication_middleware']
)
class renderTest(TestCase):
    def setUp(self):


        #basic = User.objects.create_user(username='basic', email='basic@basic.com', password='password', is_staff=False)
        #staff = User.objects.create_user(username='staff', email='staff@staff.com', password='password', is_staff=True)
        #supa = User.objects.create_superuser('super', 'supa@supa.com', 'password')
        #anon = AnonymousUser()

        #self.users = [basic, staff, supa]        
       
        users = ['basic', 'staff', 'superuser']
        acces = {'full': '', 'partial': 'db01', 'none': 'nonexistantdatasource'}
        options = ['db01', 'db02', '']
        self.users = users
        self.access = acces
        self.options = options

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

        for i in range(10):
            owner = OwnerFactory()


        for ds in options:
            for sc in options:
                for ta in options:
                    for co in options:
                        classy = ClassyFactory.build(datasource=ds, schema=sc, table=ta, column=co)
                        classy.save(user, user)

        for i in range(200):
            classy = ClassyFactory.build()
            classy.save(user, user)    


        print(Classification.objects.all())
        print(User.objects.all())
        print(Application.objects.all())

        ''' 
        self.basic = Client()
        self.staff = Client()
        self.supa = Client()
        self.anon = Client()

        self.basic.login(username='basic', password='password')
        self.staff.login(username='staff', password='password')
        self.supa.login(username='super', password='password')
        '''

    '''        
 
    def test_index_view(self):
        index_request = self.factory.get(reverse('classy:index'))
        users = [self.anon, self.basic, self.staff, self.supa]
        tran = {self.anon: 'anon', self.basic: 'basic', self.staff: 'staff', self.supa: 'supa'}
        

        #pages = {'anon': settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete'), scope='username email', state='alskdfjl;isiejf'), 'basic': reverse('classy:home'), 'staff': reverse('classy:home'), 'supa': reverse('classy:home')}

        #print(settings.OIDC_CLIENT.authorization_url(redirect_uri=os.getenv('REDIRECT_URI') + reverse('classy:login_complete')))

        for user in users:
            request = index_request
            request.user = user
            response = index(request)
            #print(response)
            #print(response.url)
            #response.client = Client()
            #self.assertRedirects(response, pages[tran[user]], fetch_redirect_response=False)

    def test_login_complete_view(self):
        users = self.users
        for user in users:
            request = self.factory.get(reverse('classy:login_complete'))
            request.user = user
            response = login_complete(request)
            self.assertEquals(response.status_code, 403)

    def test_home_view(self):
        response_codes = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        users = self.users
        for user in users:
            request = self.factory.get(reverse('classy:home'))
            request.user = user
            response = home(request)
            self.assertEquals(response.status_code, response_codes[user])

    def test_download_view(self):
        response_codes_get = {self.anon: 302, self.basic: 302, self.staff: 302, self.supa: 302}
        response_codes_post = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}
        users = self.users
        for user in users:
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

    def test_exceptions_view(self):
        response_codes = {self.anon: 302, self.basic: 302, self.staff: 200, self.supa: 200}
        users = self.users
        for user in users:
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
        users = self.users
        for user in users:
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
        rev = Classification(
            classification='PA',
            datasource='Avengers',
            schema='endgame',
            table='hype',
            column='yeet',
            creator=self.basic,
            state='A'
            )
        rev.save(user=1, approver=1)
        d1,created = DataAuthorization.objects.get_or_create(
                name='All',
            )
        users = self.users
        for user in users:
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

        d1,created = DataAuthorization.objects.get_or_create(
                name='All',
            )
        data = self.data
        users = self.users
        for user in users:
            data['column'] = data['column'] + 'c'
            form = ClassificationForm(data)
            if form.is_valid():
                rev = form.save(self.basic.pk, self.basic.pk)
            toMod = json.dumps([{"id": rev.pk, "classy": "Personal", "proty": "Protected B", "own": "---------"}])
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
                #self.assertEquals(rev.classification, clas)
                self.assertEquals(rev.state, 'A')
            elif user.is_authenticated:
                self.assertEquals(rev.state, 'A')
            else:
                self.assertEquals(rev.state, 'A')

            request = self.factory.post(reverse('classy:modi'), data={'toDel': toDel})
            request.user = user
            response = modi(request)
            self.assertEquals(response.status_code, response_codes_post[user])

            if user.is_staff:
                rev.refresh_from_db()
                self.assertEquals(rev.state, 'A')
            elif user.is_authenticated:
                self.assertEquals(rev.state, 'A')
            else:
                self.assertEquals(rev.state, 'A')
            
            #Anon does not have profile
            if not user.is_active:
                continue

            user.profile.data_authorizations.add(d1)
            user.profile.save()

            request = self.factory.post(reverse('classy:modi'), data={'toMod': toMod})
            request.user = user
            response = modi(request)
            self.assertEquals(response.status_code, response_codes_post[user])

            rev.refresh_from_db()
            if user.is_staff:
                self.assertEquals(rev.classification, "PE")
                self.assertEquals(rev.protected_type, "PB")
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

    '''

    def test_search_view(self):
        #response_codes_get = {self.anon: 302, self.basic: 200, self.staff: 200, self.supa: 200}

        for user in User.objects.all():
            c = Client()
            c.force_login(user)
   
            classy = ClassyFactory.stub()
            print(vars(classy))

        '''
        clients = self.clients

        for client in clients:
            for i in range(10):
                classy = ClassyFactory.stub()
                response = client.get(reverse('classy:search'), data=vars(classy))
                self.assertEquals(response.status_code, response_codes_get[client])
                #print(len(response.content)) 

        users = self.users
        for user in users:
            d1,created = DataAuthorization.objects.get_or_create(
                name="All",
            )
            user.profile.data_authorizations.add(d1)
            user.save()
                  
        for client in clients:
            for i in range(10):
                classy = ClassyFactory.stub()
                response = client.get(reverse('classy:search'), data=vars(classy))
                self.assertEquals(response.status_code, response_codes_get[client])
                #print(len(response.content)) 
        '''
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
