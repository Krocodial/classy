from django import forms
import datetime
from django.forms import ModelForm
from .models import classification, classification_count, classification_exception, classification_logs, classification_review_groups, classification_review
from django.contrib.auth.models import Permission
from django.conf import settings

class UploadFileForm(forms.Form):
	#title = forms.CharField(max_length=50)
	file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))

class thread:
	def __init__(self, name, start, state, user):
		self.name = name
		self.start = start
		self.state = state
		self.uptime = 0
		self.user = user
		self.progress = 0

class basic_search(forms.Form):
    query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your query'}))

class advancedSearch(forms.Form):
	
	classi_choices = (
		('Unclassified', 'Unclassified'),
		('PUBLIC', 'PUBLIC'),
		('CONFIDENTIAL', 'CONFIDENTIAL'),
		('PROTECTED A', 'PROTECTED A'),
		('PROTECTED B', 'PROTECTED B'),
		('PROTECTED C', 'PROTECTED C'),
	)
	data_source = forms.CharField(required=False, label='Datasource', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	schema = forms.CharField(required=False, label='Schema', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	table = forms.CharField(required=False, label='Table', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	column = forms.CharField(required=False, label='Column', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
	#classi = forms.ChoiceField(required=False, choices=classi_choices, widget=forms.Select(attrs={'class': 'form-control'}))
	classi = forms.MultipleChoiceField(required=False, choices=classi_choices, widget=forms.SelectMultiple(attrs={'class':'form-control'}))

	query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What would you like to search for?', 'aria-describedby': 'descript'}))
	state_choices = (
		('Inactive', 'Inactive'),
		('Active', 'Active'),
		('Pending', 'Pending'),
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

class new_tuple(forms.Form):
	process = forms.CharField(max_length=100)

class permissionForm(ModelForm):
        class Meta:
                model = Permission
                fields = ['name', 'content_type', 'codename']

class ClassificationForm(ModelForm):
	class Meta:
		model = classification
		fields = ['classification_name', 'schema', 'table_name', 'column_name', 'category', 'datasource_description', 'created_by', 'state']

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
        fields = ['classy', 'action_flag', 'n_classification', 'o_classification', 'user_id', 'state', 'approved_by']

class classificationReviewGroupForm(ModelForm):
    class Meta:
        model = classification_review_groups
        fields = ['user']

class classificationReviewForm(ModelForm):
    class Meta:
        model = classification_review
        fields = ['classy', 'group', 'classification_name', 'schema', 'table_name', 'column_name', 'datasource_description', 'action_flag', 'o_classification']





