# Generated by Django 2.0.1 on 2018-03-06 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0025_auto_20180306_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification_logs',
            name='classy_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.classification'),
        ),
    ]
