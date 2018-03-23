from django.db import models
import datetime
from django.utils import timezone

# Create your models here.

class classification(models.Model):
    classification_choices = (
	('Unclassified', 'unclassified'),
	('PUBLIC', 'public'),
        ('CONFIDENTIAL', 'confidential'),
        ('PROTECTED A', 'protected_a'),
        ('PROTECTED B', 'protected_b'),
	('PROTECTED C', 'protected_c'),
    )
    classification_name = models.CharField(max_length=50, choices=classification_choices, default='unclassified')
    schema = models.CharField(max_length=50, null=True)
    table_name = models.CharField(max_length=50, null=True)
    column_name = models.CharField(max_length=50, null=True)
    category = models.CharField(max_length=40, null=True)
    datasource_description = models.CharField(max_length=200, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=50, null=True)

    state_choices = (
    ('Active', 0),
    ('Inactive', 1),
    ('Pending Review', 2),
    )

    state = models.CharField(max_length=15, choices=state_choices, default=0)

    #date_added = models.DateTimeField(auto_now_add=True)
    #date_last_updated = models.DateTimeField(auto_now=True)

class classification_logs(models.Model):
	classy = models.ForeignKey(classification, on_delete=models.CASCADE)
	action_time = models.DateTimeField(auto_now_add=True)
	action_flag = models.SmallIntegerField()
	n_classification = models.CharField(max_length=50, null=True)
	o_classification = models.CharField(max_length=50, null=True)
	user_id = models.CharField(max_length=100, null=True)
	state = models.CharField(max_length=15, null=True)

class classification_review_groups(models.Model):
	user = models.CharField(max_length=50, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)


class classification_review(models.Model):
	classy = models.ForeignKey(classification, on_delete=models.CASCADE)
	group = models.ForeignKey(classification_review_groups, on_delete=models.CASCADE, null=True)
	classification_name = models.CharField(max_length=50, null=True)
	schema = models.CharField(max_length=50, null=True)
	table_name = models.CharField(max_length=50, null=True)
	column_name = models.CharField(max_length=50, null=True)
	datasource_description = models.CharField(max_length=100, null=True)
	action_flag = models.SmallIntegerField()
	o_classification = models.CharField(max_length=50, null=True)

