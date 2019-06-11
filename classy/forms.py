from django import forms
from django.forms import ModelForm

from django.utils.translation import gettext_lazy as _

from .models import *
from .models import classification_choices


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document',)
        #file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))

class Thread:
    def __init__(self, running):
        self.name = ''
        self.running = running

class BasicSearch(forms.Form):
    #query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your query'}))
    query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What would you like to search for?', 'aria-describedby': 'descript'}))

class AdvancedSearch(ModelForm):
    
    datasource = forms.CharField(required=False, label='Datasource', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    schema = forms.CharField(required=False, label='Schema', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    table = forms.CharField(required=False, label='Table', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    column = forms.CharField(required=False, label='Column', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Classification
        exclude = ['created', 'creator', 'masking', 'notes']
        help_texts = {
            'classification': _('Help text'),
        }
        labels = {
            'owner': _('Application')
        }
        widgets = {
            'classification': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),
            'protected_type': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),
            'owner': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),
            'state': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),
        }



'''
class AdvancedSearch(forms.Form):
    
    classi_choices = (
        ('UN', 'Unclassified'),
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
    classi = forms.MultipleChoiceField(required=False, choices=classification_choices, widget=forms.SelectMultiple(attrs={'class':'form-control'}))

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
    size = forms.ChoiceField(required=False, choices=size_choices, widget=forms.Select(attrs={'class': 'custom-select custom-select-sm', 'onchange': 'this.form.submit();'}))

'''

class LoginForm(forms.Form):
    if settings.BYPASS_AUTH:
        username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'AUTOCOMPLETE': 'off'}))

class ClassificationForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'datasource', 'schema', 'table', 'column', 'creator', 'state', 'masking', 'notes']

class ClassificationCountForm(ModelForm):
    class Meta:
        model = ClassificationCount
        fields = ['classification', 'count', 'date', 'user']   

class ClassificationLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'flag', 'classification', 'protected_type', 'user', 'state', 'approver']

class ClassificationReviewGroupForm(ModelForm):
    class Meta:
        model = ClassificationReviewGroups
        fields = ['user']

class ClassificationReviewForm(ModelForm):
    class Meta:
        model = ClassificationReview
        fields = ['classy', 'group', 'classification', 'flag']

class LogDetailForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['classification', 'protected_type']

class LogDetailMNForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['masking', 'notes']

class ClassificationFullLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'previous_log', 'flag', 'classification', 'protected_type', 'user', 'state', 'approver', 'masking_change', 'note_change']

