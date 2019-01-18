from .models import *

def wildcard_handler(auth):
    permitted = classification.objects.none()

    if auth.datasource == '':
        tmp = classification.objects.filter(
            datasource__icontains=auth.datasource)
    else:
        tmp = classification.objects.filter(
            datasource__iexact=auth.datasource)
    permitted = tmp

    if auth.schema == '':
        tmp = classification.objects.filter(
            schema__icontains=auth.schema)
    else:
        tmp = classification.objects.filter(
            schema__iexact=auth.schema)
    permitted = permitted & tmp

    if auth.table == '':
        tmp =  classification.objects.filter(
            table__icontains=auth.table)
    else:
        tmp = classification.objects.filter(
            table__iexact=auth.table)
    permitted = permitted & tmp

    if auth.column == '':
        tmp = classification.objects.filter(
            column__icontains=auth.column)
    else:
        tmp = classification.objects.filter(
            column__iexact=auth.column)
   
    permitted = permitted & tmp

    return permitted

def group_deconstructor(permitted, group):
    for auth in group:
        permitted = permitted | wildcard_handler(auth)

    return permitted

def query_constructor(queryset, user):
    user = user.profile
    permitted = classification.objects.none()

    for auth in user.data_authorizations.all():
        permitted = permitted | wildcard_handler(auth)

    for group in user.dataset_authorizations.all():
        permitted = group_deconstructor(permitted, group) 

    return queryset & permitted

