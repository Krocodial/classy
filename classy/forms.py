from django import forms
from django.forms import ModelForm

from django.utils.translation import gettext_lazy as _

from .models import *
from .models import classification_choices, state_choices, protected_series

size_choices = (
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (100, '100'),)

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document',)
        #file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))

class Thread:
    def __init__(self, running):
        self.name = ''
        self.running = running

clas_mod_options = tuple([(u'', '---------')] + list(classification_choices))
prot_mod_options = tuple([(u'', '---------')] + list(protected_series))

class ModifyForm(ModelForm):

    classification = forms.ChoiceField(required=False, choices=clas_mod_options, widget=forms.Select(attrs={'class': 'form-control'}))
    protected_type = forms.ChoiceField(required=False, choices=prot_mod_options, widget=forms.Select(attrs={'class': 'form-control'}))
    owner = forms.ModelChoiceField(queryset=Application.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner']

    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            if protected_type != '':
                raise forms.ValidationError(
                    "Is this really protected?"
                )

class BasicSearch(forms.Form):
    #query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your query'}))
    query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What would you like to search for?', 'aria-describedby': 'descript'}))
    size = forms.ChoiceField(initial=10, required=False, choices=size_choices, widget=forms.Select(attrs={'class': 'custom-select custom-select-sm', 'onchange': 'this.form.submit();'}))

class AdvancedSearch(forms.Form):
 
    datasource = forms.CharField(initial='', required=False, label='Datasource', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    schema = forms.CharField(initial='', required=False, label='Schema', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    table = forms.CharField(initial='', required=False, label='Table', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    column = forms.CharField(initial='', required=False, label='Column', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    classification = forms.MultipleChoiceField(initial=[i[0] for i in Classification._meta.get_field('classification').flatchoices], required=False, choices=classification_choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    protected_type = forms.MultipleChoiceField(required=False, choices=protected_series, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    state = forms.MultipleChoiceField(initial=['A', 'P'], required=False, choices=state_choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    #size for pagination
    owner = forms.ModelMultipleChoiceField(queryset=Application.objects.all(), required=False, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

class LoginForm(forms.Form):
    if settings.BYPASS_AUTH:
        username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'AUTOCOMPLETE': 'off'}))

class ClassificationForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'datasource', 'schema', 'table', 'column', 'creator', 'state', 'masking', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            if protected_type != '':
                raise forms.ValidationError(
                    "Is this really protected?"
                )

class ClassificationCountForm(ModelForm):
    class Meta:
        model = ClassificationCount
        fields = ['classification', 'protected_type', 'count', 'date', 'user']   

class ClassificationLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'flag', 'classification', 'protected_type', 'previous_log', 'owner', 'user', 'state', 'approver']

class ClassificationReviewGroupForm(ModelForm):
    class Meta:
        model = ClassificationReviewGroups
        fields = ['user']

class ClassificationReviewForm(ModelForm):
    class Meta:
        model = ClassificationReview
        fields = ['classy', 'group', 'classification', 'protected_type', 'owner', 'flag']

class LogDetailForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['classification', 'protected_type']
    
    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            if protected_type != '':
                raise forms.ValidationError(
                    "Is this really protected?"
                )


class LogDetailMNForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['masking', 'notes']

class ClassificationFullLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'previous_log', 'flag', 'classification', 'protected_type', 'user', 'state', 'approver', 'masking_change', 'note_change']

