from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from .models import Application, DataAuthorization, DatasetAuthorization, Profile, ClassificationCount, Classification, ClassificationLogs, ClassificationReviewGroups, ClassificationReview, Document, classification_choices, state_choices, protected_series
#from .models import classification_choices, state_choices, protected_series

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
    owner = forms.ModelChoiceField(
                    queryset=Application.objects.all(), 
                    required=False, 
                    label="Application",
                    help_text="What application does this data belong to?",
                    widget=forms.Select(attrs={'class': 'form-control'}))

    dependents = forms.ModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label="Dependencies",
        help_text="What applications rely on this data?",
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    
    state = forms.ChoiceField(required=False, label='', choices=state_choices, widget=forms.HiddenInput())



    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'dependents', 'state']

    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            if protected_type != '':
                protected_type = ''
                #raise forms.ValidationError(
                #    "Public or Unclassified cannot be protected"
                #)

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
    owner = forms.ModelMultipleChoiceField(queryset=Application.objects.all(), required=False, label="Application", widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

class LoginForm(forms.Form):
    if settings.BYPASS_AUTH:
        username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'AUTOCOMPLETE': 'off'}))


class ClassificationForm(ModelForm):

    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'dependents', 'datasource', 'schema', 'table', 'column', 'creator', 'state', 'masking', 'notes']

    #For usability, don't deny this change just adjust is according to standards. 
    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            protected_type = ''
        
    def save(self, user, approver):
        classy = super(ClassificationForm, self).save(commit=False)
        classy.save(user, approver)
        for dep in self.cleaned_data['dependents']:
            classy.dependents.add(dep.pk)
        return classy

class ClassificationCountForm(ModelForm):
    class Meta:
        model = ClassificationCount
        fields = ['classification', 'protected_type', 'count', 'date', 'user']   

#It might seem like this isn't used, but it's used by the Classification model for auto-log generation
class ClassificationLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'flag', 'classification', 'protected_type', 'owner', 'dependents', 'user', 'state', 'approver', 'masking_change', 'note_change']

    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            protected_type = ''

class LogDetailSubmitForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'dependents', 'notes', 'masking', 'state']

    def save(self, user, approver):
        classy = super(LogDetailSubmitForm, self).save(commit=False)
        classy.save(user, approver)
        return classy

class LogDetailForm(ModelForm):
    
    classification = forms.ChoiceField(required=False, choices=clas_mod_options, widget=forms.Select(attrs={'class': 'form-control input-sm'}))
    protected_type = forms.ChoiceField(required=False, choices=prot_mod_options, widget=forms.Select(attrs={'class': 'form-control input-sm'}))
    owner = forms.ModelChoiceField(
                    queryset=Application.objects.all(), 
                    required=False, 
                    label="Application",
                    widget=forms.Select(attrs={'class': 'form-control input-sm'}))

    dependents = forms.ModelMultipleChoiceField(
        queryset=Application.objects.all(),
        required=False,
        label="Dependencies",
        widget=forms.SelectMultiple(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = Classification
        fields = ['classification', 'protected_type', 'owner', 'dependents']
    
    def clean(self):
        cleaned_data = super().clean()
        classification = cleaned_data.get("classification")
        protected_type = cleaned_data.get("protected_type")
        if classification == 'UN' or classification == 'PU':
            if protected_type != '':
                raise forms.ValidationError(
                    "Is this really protected?"
                )


    def save(self, user, approver):
        classy = super(LogDetailForm, self).save(commit=False)
        classy.save(user, approver)
        return classy



class ClassificationReviewGroupForm(ModelForm):
    class Meta:
        model = ClassificationReviewGroups
        fields = ['user']

class ClassificationReviewForm(ModelForm):
    class Meta:
        model = ClassificationReview
        fields = ['classy', 'group', 'classification', 'protected_type', 'owner', 'flag']

class LogDetailMNForm(ModelForm):
    class Meta:
        model = Classification
        fields = ['masking', 'notes']

class ClassificationFullLogForm(ModelForm):
    class Meta:
        model = ClassificationLogs
        fields = ['classy', 'flag', 'classification', 'protected_type', 'owner', 'user', 'state', 'approver', 'masking_change', 'note_change']

