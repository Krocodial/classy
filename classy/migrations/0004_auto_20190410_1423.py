# Generated by Django 2.0.12 on 2019-04-10 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0003_auto_20190205_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification_logs',
            name='masking_change',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='classification_logs',
            name='note_change',
            field=models.TextField(blank=True),
        ),
    ]