from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class data_authorization(models.Model):

    name = models.CharField(max_length=255, unique=True, blank=True)
    datasource = models.CharField(max_length=100, blank=True)
    schema = models.CharField(max_length=100, blank=True)
    table = models.CharField(max_length=100, blank=True)
    column = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Data Authorization')
        verbose_name_plural = _('Data Authorizations')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = self.datasource + '/' + self.schema + '/' + self.table + '/' + self.column
        super(data_authorization, self).save(*args, **kwargs)

class dataset_authorization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data_authorizations = models.ManyToManyField(
        data_authorization,
        verbose_name=_('Data Authorization'),
        blank=True,
    )

    class Meta:
        verbose_name = _('Dataset Authorization')
        verbose_name_plural = _('Dataset Authorizations')

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True)
    data_authorizations = models.ManyToManyField(
        data_authorization,
        verbose_name=_('Data Authorizations'),
        blank=True,
    )
    dataset_authorizations = models.ManyToManyField(
        dataset_authorization,
        verbose_name=_('Dataset Authorizations'),
        blank=True,
    )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class classification_count(models.Model):
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    count = models.BigIntegerField()
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        default_permissions = ()

class classification(models.Model):
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    datasource = models.CharField(max_length=100)
    schema = models.CharField(max_length=100)
    table = models.CharField(max_length=100)
    column = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    state = models.CharField(max_length=1, choices=state_choices)
    masking = models.CharField(max_length=200, blank=True)
    notes = models.CharField(max_length=400, blank=True)
    
class classification_exception(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.CASCADE)
    
    class Meta:
        default_permissions = ()

class classification_logs(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)
    flag = models.SmallIntegerField()
    new_classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    old_classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Modifier')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Approver')
    state = models.CharField(max_length=1, choices=state_choices)
    masking_change = models.TextField(blank=True)
    note_change = models.TextField(blank=True)

    class Meta:
        default_permissions = ()

class classification_review_groups(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()

class classification_review(models.Model):
    classy = models.ForeignKey(classification, on_delete=models.CASCADE)
    group = models.ForeignKey(classification_review_groups, on_delete=models.CASCADE)
    classification_name = models.CharField(max_length=2, choices=classification_choices)
    flag = models.SmallIntegerField()
    
    class Meta:
        default_permissions = ()
        permissions = (("can_review", "Can review & accept user changes"),)

class Document(models.Model):
    document = models.FileField()
    uploaded_at = models.DateField(auto_now_add=True)

