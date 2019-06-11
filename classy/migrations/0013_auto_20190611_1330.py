# Generated by Django 2.1.8 on 2019-06-11 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0012_auto_20190607_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classificationlogs',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='classy.Classification'),
        ),
        migrations.AlterField(
            model_name='classificationreview',
            name='classy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.Classification'),
        ),
    ]
