# Generated by Django 2.1.8 on 2019-06-21 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0010_auto_20190620_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificationcount',
            name='protected_type',
            field=models.CharField(blank=True, choices=[('PA', 'Protected A'), ('PB', 'Protected B'), ('PC', 'Protected C')], max_length=2),
        ),
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
