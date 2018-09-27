# Generated by Django 2.0.7 on 2018-09-06 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0036_classification_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification',
            name='classification_name',
            field=models.CharField(choices=[('Unclassified', 'unclassified'), ('PUBLIC', 'public'), ('CONFIDENTIAL', 'confidential'), ('PROTECTED A', 'protected_a'), ('PROTECTED B', 'protected_b'), ('PROTECTED C', 'protected_c')], max_length=50),
        ),
    ]
