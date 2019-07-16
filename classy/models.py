from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

classification_choices = (
    ("UN", "Unclassified"),
    ("PU", "Public"),
    ("PE", "Personal"),
    ("CO", "Confidential")
)

protected_series = (
    ('PA', 'Protected A'),
    ('PB', 'Protected B'),
    ('PC', 'Protected C')
)

state_choices = (
    ("A", "Active"),
    ("I", "Inactive"),
    ("P", "Pending")
    )

#Defined during development and now heavily integrated in JS Ajax calls
flag_choices = (
    (0, 'Delete'),
    (1, 'Modify'),
    (2, 'Create')
)

queues = (
    ('uploads', 'Uploads'),
    ('counter', 'Counter')
)

class Application(models.Model):
    acronym = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    poc = models.CharField(max_length=100, blank=True, help_text='Point of contact for the application')
    description = models.TextField(max_length=300, blank=True)
    
    def __str__(self):
        return self.name


class DataAuthorization(models.Model):

    name = models.CharField(max_length=255, unique=True, blank=True)
    datasource = models.CharField(max_length=100, blank=True)
    schema = models.CharField(max_length=100, blank=True)
    table = models.CharField(max_length=100, blank=True)
    column = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name == '':
            self.name = self.datasource + '/' + self.schema + '/' + self.table + '/' + self.column
        super(DataAuthorization, self).save(*args, **kwargs)

class DatasetAuthorization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data_authorizations = models.ManyToManyField(
        DataAuthorization,
        verbose_name=_('Permission'),
        blank=True,
    )
    
    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_authorizations = models.ManyToManyField(
        DataAuthorization,
        verbose_name=_('Permissions'),
        blank=True,
    )
    dataset_authorizations = models.ManyToManyField(
        DatasetAuthorization,
        verbose_name=_('Groups'),
        blank=True,
    )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _('user Authorization')
        verbose_name_plural = _('user Authorizations')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ClassificationCount(models.Model):
    classification = models.CharField(max_length=2, choices=classification_choices)
    protected_type = models.CharField(max_length=2, choices=protected_series, blank=True)
    count = models.BigIntegerField()
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        default_permissions = ()

class Classification(models.Model):
    classification = models.CharField(max_length=2, choices=classification_choices, default='UN')
    protected_type = models.CharField(max_length=2, choices=protected_series, blank=True)
    owner = models.ForeignKey(Application, verbose_name="application", on_delete=models.PROTECT, blank=True, null=True)
    datasource = models.CharField(max_length=100)
    schema = models.CharField(max_length=100)
    table = models.CharField(max_length=100)
    column = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    state = models.CharField(max_length=1, choices=state_choices)
    masking = models.CharField(max_length=200, blank=True)
    notes = models.CharField(max_length=400, blank=True)

    class Meta:
        unique_together = [['datasource', 'schema', 'table', 'column']]

    
    def __str__(self):
        return self.datasource + '/' + self.schema + '/' + self.table + '/' + self.column

    def clean(self):
        if self.classification == "UN" or self.classification =="PU":
            self.protected_type = ''
            #if self.protected_type != '':
            #    raise ValidationError("Unclassified or Public cannot be protected")         
 
class ClassificationLogs(models.Model):
    classy = models.ForeignKey(Classification, on_delete=models.CASCADE)
    #previous_log = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    flag = models.SmallIntegerField(choices=flag_choices)
    classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    protected_type = models.CharField(max_length=2, choices=protected_series, blank=True)
    owner = models.ForeignKey(Application, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Modifier')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Approver')
    state = models.CharField(max_length=1, choices=state_choices)
    masking_change = models.TextField(blank=True)
    note_change = models.TextField(blank=True)

    class Meta:
        default_permissions = ()

    def clean(self):
        if self.classification == "UN" or self.classification =="PU":
            self.protected_type = ''


class ClassificationReviewGroups(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()

class ClassificationReview(models.Model):
    classy = models.ForeignKey(Classification, on_delete=models.CASCADE)
    group = models.ForeignKey(ClassificationReviewGroups, on_delete=models.CASCADE)
    classification = models.CharField(max_length=2, choices=classification_choices, blank=True)
    protected_type = models.CharField(max_length=2, choices=protected_series, blank=True)
    owner = models.ForeignKey(Application, on_delete=models.CASCADE, blank=True, null=True)
    flag = models.SmallIntegerField(choices=flag_choices)
    
    class Meta:
        default_permissions = ()
        permissions = (("can_review", "Can review & accept user changes"),)


class Document(models.Model):
    document = models.FileField()
    uploaded_at = models.DateField(auto_now_add=True)

def get_email(self):
    return self.email

User.add_to_class("__str__", get_email)
