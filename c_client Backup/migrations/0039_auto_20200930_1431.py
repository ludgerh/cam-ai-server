# Generated by Django 3.1 on 2020-09-30 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0038_auto_20200930_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='view',
            name='ibn',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='view',
            name='ibt',
            field=models.CharField(default='', max_length=2),
        ),
        migrations.AddField(
            model_name='view',
            name='obn',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='view',
            name='obt',
            field=models.CharField(default='', max_length=2),
        ),
    ]