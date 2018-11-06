from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

classification_choices = (
    ('UN', 'unclassified'),
    ('PU', 'public'),
    ('CO', 'confidential'),
    ('PA', 'protected a'),
    ('PB', 'protected b'),
    ('PC', 'protected c')
    )

state_choices = (
    ('A', 'Active'),
    ('I', 'Inactive'),
    ('P', 'Pending')
    )

queues = (
    ('uploads', 'Uploads'),
    ('counter', 'Counter')
)

class task(models.Model):
    name = models.CharField(max_length=100)
    verbose_name = models.TextField(max_length=200, blank=True)
    priority = models.SmallIntegerField(default=0, help_text='Higher priority tasks will be executed first')
    run_at = models.DateTimeField(auto_now=True)
    queue = models.CharField(max_length=7, choices=queues)
    error = models.TextField(blank=True, help_text='This will show why the task has failed')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    progress = models.FloatField(blank=True)
    class Meta:
        default_permissions = ()

class completed_task(models.Model):
    name = models.CharField(max_length=100)
    verbose_name = models.TextField(max_length=200, blank=True)
    priority = models.SmallIntegerField(default=0, help_text='Higher priority tasks will be executed first')
    run_at = models.DateTimeField()
    queue = models.CharField(max_length=7, choices=queues)
    finished_at = models.DateTimeField(auto_now=True)
    error = models.TextField(blank=True, help_text='This will show why the task has failed')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    class Meta:
        default_permissions = ()

class classification_count(models.Model):
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    count = models.BigIntegerField()
    date = models.DateField()

class classification(models.Model):
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    datasource = models.CharField(max_length=100)
    schema = models.CharField(max_length=50)
    table = models.CharField(max_length=50)
    column = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    state = models.CharField(max_length=1, choices=state_choices)
    masking = models.CharField(max_length=600, null=True)

class classification_exception(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.CASCADE)

class classification_logs(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)
    flag = models.SmallIntegerField()
    new_classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    old_classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Modifier')
    approver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Approver')
    state = models.CharField(max_length=1, choices=state_choices)

class classification_review_groups(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)


class classification_review(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.CASCADE)
    group = models.ForeignKey(classification_review_groups, on_delete=models.CASCADE)
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    flag = models.SmallIntegerField()
