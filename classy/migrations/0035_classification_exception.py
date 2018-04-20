# Generated by Django 2.0.4 on 2018-04-19 04:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0034_classification_logs_approved_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='classification_exception',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classy.classification')),
            ],
        ),
    ]
