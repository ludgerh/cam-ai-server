# Generated by Django 3.1 on 2020-09-09 11:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0013_auto_20200909_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfmodel',
            name='lastclean',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 9, 13, 5, 8, 496099)),
        ),
        migrations.AlterField(
            model_name='tfmodel',
            name='lastfile',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 9, 13, 5, 8, 496081)),
        ),
    ]