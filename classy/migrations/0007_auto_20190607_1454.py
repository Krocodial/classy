# Generated by Django 2.1.8 on 2019-06-07 21:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classy', '0006_auto_20190529_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acronym', models.CharField(blank=True, max_length=20, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('poc', models.CharField(blank=True, help_text='Point of contact for the application', max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classification', models.CharField(choices=[('UN', 'unclassified'), ('PU', 'public'), ('PE', 'personal'), ('CO', 'confidential')], max_length=2)),
                ('count', models.BigIntegerField()),
                ('date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ClassificationLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('flag', models.SmallIntegerField(choices=[(0, 'Delete'), (1, 'Modify'), (2, 'Create')])),
                ('classification', models.CharField(blank=True, choices=[('UN', 'unclassified'), ('PU', 'public'), ('PE', 'personal'), ('CO', 'confidential')], max_length=2)),
                ('protected_type', models.CharField(blank=True, choices=[('PA', 'protected a'), ('PB', 'protected b'), ('PC', 'protected c')], max_length=2)),
                ('state', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive'), ('P', 'Pending')], max_length=1)),
                ('masking_change', models.TextField(blank=True)),
                ('note_change', models.TextField(blank=True)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Approver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ClassificationReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classification', models.CharField(choices=[('UN', 'unclassified'), ('PU', 'public'), ('PE', 'personal'), ('CO', 'confidential')], max_length=2)),
                ('flag', models.SmallIntegerField()),
            ],
            options={
                'permissions': (('can_review', 'Can review & accept user changes'),),
                'default_permissions': (),
            },
        ),
        migrations.RenameModel(
            old_name='data_authorization',
            new_name='DataAuthorization',
        ),
        migrations.RenameModel(
            old_name='dataset_authorization',
            new_name='DatasetAuthorization',
        ),
        migrations.RemoveField(
            model_name='classification_count',
            name='user',
        ),
        migrations.RemoveField(
            model_name='classification_exception',
            name='classy',
        ),
        migrations.RemoveField(
            model_name='classification_logs',
            name='approver',
        ),
        migrations.RemoveField(
            model_name='classification_logs',
            name='classy',
        ),
        migrations.RemoveField(
            model_name='classification_logs',
            name='user',
        ),
        migrations.RemoveField(
            model_name='classification_review',
            name='classy',
        ),
        migrations.RemoveField(
            model_name='classification_review',
            name='group',
        ),
        migrations.RemoveField(
            model_name='classification',
            name='classification_name',
        ),
        migrations.AddField(
            model_name='classification',
            name='classification',
            field=models.CharField(choices=[('UN', 'unclassified'), ('PU', 'public'), ('PE', 'personal'), ('CO', 'confidential')], default='UN', max_length=2),
        ),
        migrations.AddField(
            model_name='classification',
            name='protected_type',
            field=models.CharField(blank=True, choices=[('PA', 'protected a'), ('PB', 'protected b'), ('PC', 'protected c')], max_length=2),
        ),
        migrations.RenameModel(
            old_name='classification_review_groups',
            new_name='ClassificationReviewGroups',
        ),
        migrations.DeleteModel(
            name='classification_count',
        ),
        migrations.DeleteModel(
            name='classification_exception',
        ),
        migrations.DeleteModel(
            name='classification_logs',
        ),
        migrations.DeleteModel(
            name='classification_review',
        ),
        migrations.AddField(
            model_name='classificationreview',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.Classification'),
        ),
        migrations.AddField(
            model_name='classificationreview',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.ClassificationReviewGroups'),
        ),
        migrations.AddField(
            model_name='classificationlogs',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.Classification'),
        ),
        migrations.AddField(
            model_name='classificationlogs',
            name='previous_log',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='classy.ClassificationLogs'),
        ),
        migrations.AddField(
            model_name='classificationlogs',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Modifier', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classification',
            name='owner',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.PROTECT, to='classy.Application'),
            preserve_default=False,
        ),
    ]
