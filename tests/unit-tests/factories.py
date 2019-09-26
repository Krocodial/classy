from classy.models import Application, Classification, DataAuthorization
from django.contrib.auth.models import User
from django.conf import settings

import factory

from classy.models import classification_choices, protected_series, state_choices

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
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: 'user' + str(n))
    email = factory.Sequence(lambda n: 'user' + str(n) + '@email.com')
    is_staff = False
    is_superuser = False


class ClassyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Classification

    datasource = factory.Faker('sentence', nb_words=4)
    schema = factory.Faker('sentence', nb_words=4)
    table = factory.Faker('sentence', nb_words=4)
    column = factory.Faker('sentence', nb_words=4)

    classification = factory.Faker('random_element', elements=[x[0] for x in classification_choices])
    protected_type = factory.Faker('random_element', elements=[x[0] for x in protected_series])
    #When downloading/searching the default is to exclude inactive state elements.
    #state = factory.Faker('random_element', elements=[x[0] for x in state_choices])
    state = factory.Faker('random_element', elements=['A', 'P'])    

    creator = factory.Iterator(User.objects.all())
    owner = factory.Iterator(Application.objects.all())
    
    #creator = factory.SubFactory(UserFactory)
    #owner = factory.Iterator(Application.objects.all())

