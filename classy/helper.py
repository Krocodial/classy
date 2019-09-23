from .models import Classification
import os
from django.contrib.auth import logout
from .forms import AdvancedSearch, BasicSearch


def role_checker(user, payload, request):

    try:
        roles = payload.get('resource_access').get(os.getenv('SSO_CLIENT_ID')).get('roles')
    except:
        roles = []
    if 'superuser' in roles:
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
    elif 'staff' in roles:
        user.is_active = True
        user.is_staff = True
        user.is_superuser = False
        user.save()
    elif 'basic' in roles:
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()
    else:
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()
        if request.user.is_authenticated:
            logout(request)

def wildcard_handler(auth):

    if auth.datasource == '':
        tmp = Classification.objects.filter(
            datasource__icontains=auth.datasource)
    else:
        tmp = Classification.objects.filter(
            datasource__iexact=auth.datasource)
    permitted = tmp

    if auth.schema == '':
        tmp = Classification.objects.filter(
            schema__icontains=auth.schema)
    else:
        tmp = Classification.objects.filter(
            schema__iexact=auth.schema)
    permitted = permitted & tmp
    #permitted = permitted.intersection(tmp)

    if auth.table == '':
        tmp =  Classification.objects.filter(
            table__icontains=auth.table)
    else:
        tmp = Classification.objects.filter(
            table__iexact=auth.table)
    permitted = permitted & tmp
    #permitted = permitted.intersection(tmp)

    if auth.column == '':
        tmp = Classification.objects.filter(
            column__icontains=auth.column)
    else:
        tmp = Classification.objects.filter(
            column__iexact=auth.column)
   
    permitted = permitted & tmp
    #permitted = permitted.intersection(tmp)

    return permitted

def group_deconstructor(permitted, group):
    for auth in group.data_authorizations.all():
        permitted = permitted | wildcard_handler(auth)
        #permitted = permitted.union(wildcard_handler(auth))

    return permitted

def query_constructor(queryset, user):
    user = user.profile
    permitted = Classification.objects.none()
    queryset = queryset.distinct()


    for auth in user.data_authorizations.all():
        #permitted = permitted.union(wildcard_handler(auth))
        permitted = permitted | wildcard_handler(auth)

    for group in user.dataset_authorizations.all():
        permitted = group_deconstructor(permitted, group) 

    permitted = permitted.distinct()

    return queryset & permitted
    #return queryset.intersection(permitted)




def filter_results(request, data):
    advanced = AdvancedSearch(data)
    basic = BasicSearch(data)
    if advanced.is_valid() and basic.is_valid():
        classification = advanced.cleaned_data['classification']
        protected_type = advanced.cleaned_data['protected_type']
        owner =         advanced.cleaned_data['owner']
        state =         advanced.cleaned_data['state']

        #if no classification is chosen search all of them
        if len(classification) == 0:
            classification = [i[0] for i in Classification._meta.get_field('classification').flatchoices]
        #This might look weird but it's the only way to check foreign keys, as if they are empty we will be running owner__in=[] which will not give all values, but none.
        if len(protected_type) == 0:
            prot = Classification.objects.all()
        else:
            prot = Classification.objects.filter(protected_type__in=protected_type)

        if len(owner) == 0:
            own = Classification.objects.all()
        else:
            own = Classification.objects.filter(owner__pk__in=owner)

        if len(state) == 0:
            state = ['A', 'P']

        queryset = Classification.objects.filter(
            datasource__icontains=advanced.cleaned_data['datasource'],
            schema__icontains=advanced.cleaned_data['schema'],
            table__icontains=advanced.cleaned_data['table'],
            column__icontains=advanced.cleaned_data['column'],
            classification__in=classification,
            state__in=state)


        query = basic.cleaned_data['query']
        data = Classification.objects.filter(datasource__icontains=query)
        sche = Classification.objects.filter(schema__icontains=query)
        tabl = Classification.objects.filter(table__icontains=query)
        colu = Classification.objects.filter(column__icontains=query)
        stat = Classification.objects.filter(state__in=state)
        #OR the querysets to search all fields for value
        queryset2 = data | sche | tabl | colu 
        queryset = (queryset2 & queryset & stat & own & prot).distinct()

        queryset = query_constructor(queryset, request.user)
        return queryset
    else:
        return Classification.objects.none()

