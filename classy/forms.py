from django import forms
import datetime
from django.forms import ModelForm
from .models import classification

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

class advancedSearch(forms.Form):
	
	classi_choices = (
		('', 'All (default)'),
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
	classi = forms.ChoiceField(required=False, choices=classi_choices, widget=forms.Select(attrs={'class': 'form-control'}))
	query = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What would you like to search for?', 'aria-describedby': 'descript'}))
	state_choices = (
		('', 'Active/Pending (default)'),
		('Inactive', 'Inactive'),
		('Active', 'Active'),
		('Pending', 'Pending'),
	)
	stati = forms.MultipleChoiceField(required=False, choices=state_choices, widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

class loginform(forms.Form):
	username = forms.CharField(label='username', max_length=100, widget=forms.TextInput(attrs={
	'class': 'form-control', 'placeholder': 'Username'}))
	password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class new_tuple(forms.Form):
	process = forms.CharField(max_length=100)

class ClassificationForm(ModelForm):
	class Meta:
		model = classification
		fields = ['classification_name', 'schema', 'table_name', 'column_name', 'category', 'datasource_description', 'created_by', 'state']

