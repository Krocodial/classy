# Generated by Django 2.1.8 on 2019-07-23 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0008_auto_20190716_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification',
            name='dependents',
            field=models.ManyToManyField(related_name='dependant_classification', to='classy.Application'),
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
    ]
