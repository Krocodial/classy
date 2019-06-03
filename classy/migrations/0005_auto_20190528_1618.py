# Generated by Django 2.1.8 on 2019-05-28 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classy', '0004_auto_20190410_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='')),
                ('uploaded_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.SmallIntegerField(blank=True, default=0, help_text='Higher priority tasks will be executed first', null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='progress',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
