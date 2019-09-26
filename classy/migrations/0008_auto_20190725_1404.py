# Generated by Django 2.1.8 on 2019-07-25 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0007_auto_20190716_1413'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataauthorization',
            options={'verbose_name': 'Permission', 'verbose_name_plural': 'Permissions'},
        ),
        migrations.AlterModelOptions(
            name='datasetauthorization',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'user Authorization', 'verbose_name_plural': 'user Authorizations'},
        ),
        migrations.RemoveField(
            model_name='profile',
            name='location',
        ),
        migrations.AddField(
            model_name='classification',
            name='dependents',
            field=models.ManyToManyField(blank=True, related_name='dependent', to='classy.Application'),
        ),
        migrations.AddField(
            model_name='classificationlogs',
            name='dependents',
            field=models.ManyToManyField(blank=True, related_name='log_dependent', to='classy.Application'),
        ),
        migrations.AddField(
            model_name='classificationlogs',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classy.Application'),
        ),
        migrations.AlterField(
            model_name='application',
            name='description',
            field=models.TextField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='classification',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='classy.Application', verbose_name='application'),
        ),
        migrations.AlterField(
            model_name='classificationlogs',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.Classification'),
        ),
        migrations.AlterField(
            model_name='classificationreview',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.Classification'),
        ),
        migrations.AlterField(
            model_name='datasetauthorization',
            name='data_authorizations',
            field=models.ManyToManyField(blank=True, to='classy.DataAuthorization', verbose_name='Permission'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='data_authorizations',
            field=models.ManyToManyField(blank=True, to='classy.DataAuthorization', verbose_name='Permissions'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='dataset_authorizations',
            field=models.ManyToManyField(blank=True, to='classy.DatasetAuthorization', verbose_name='Groups'),
        ),
        migrations.AlterUniqueTogether(
            name='classification',
            unique_together={('datasource', 'schema', 'table', 'column')},
        ),
    ]