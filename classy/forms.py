from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.conf import settings

import datetime

from .models import *

class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))

class thread:
    def __init__(self, running):
        self.name = ''
        self.running = running

class basic_search(forms.Form):
    query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your query'}))

class advancedSearch(forms.Form):
    
    classi_choices = (
        ('UN', 'UNCLASSIFIED'),
        ('PU', 'PUBLIC'),
        ('CO', 'CONFIDENTIAL'),
        ('PA', 'PROTECTED A'),
        ('PB', 'PROTECTED B'),
        ('PC', 'PROTECTED C'),
    )
    data_source = forms.CharField(required=False, label='Datasource', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    schema = forms.CharField(required=False, label='Schema', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    table = forms.CharField(required=False, label='Table', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    column = forms.CharField(required=False, label='Column', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    classi = forms.MultipleChoiceField(required=False, choices=classi_choices, widget=forms.SelectMultiple(attrs={'class':'form-control'}))

    query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What would you like to search for?', 'aria-describedby': 'descript'}))
    state_choices = (
        ('I', 'Inactive'),
        ('A', 'Active'),
        ('P', 'Pending'),
    )
    stati = forms.MultipleChoiceField(required=False, choices=state_choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    #size for pagination
    size_choices = (
        (10, '10'),
        (25, '25'),
        (50, '50'),
        (100, '100'),
    )
    size = forms.ChoiceField(required=False, choices=size_choices, widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}))


class loginform(forms.Form):
    if settings.BYPASS_AUTH:
        username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'AUTOCOMPLETE': 'off'}))

class ClassificationForm(ModelForm):
    class Meta:
        model = classification
        fields = ['classification_name', 'datasource', 'schema', 'table', 'column', 'creator', 'state']

class classificationCountForm(ModelForm):
    class Meta:
        model = classification_count
        fields = ['classification_name', 'count', 'date']   

class classificationExceptionForm(ModelForm):
    class Meta:
        model = classification_exception
        fields = ['classy']

class classificationLogForm(ModelForm):
    class Meta:
        model = classification_logs
        fields = ['classy', 'flag', 'new_classification', 'old_classification', 'user', 'state', 'approver']

class classificationReviewGroupForm(ModelForm):
    class Meta:
        model = classification_review_groups
        fields = ['user']

class classificationReviewForm(ModelForm):
    class Meta:
        model = classification_review
        fields = ['classy', 'group', 'classification_name', 'flag']

class taskForm(ModelForm):
    class Meta:
        model = task
        fields = ['name', 'verbose_name', 'priority', 'queue', 'error', 'user', 'progress']

class completed_taskForm(ModelForm):
    class Meta:
        model = completed_task
        fields = ['name', 'verbose_name', 'priority', 'run_at', 'queue', 'error', 'user']

