# Generated by Django 3.1 on 2020-09-09 11:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0018_auto_20200909_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='tfmodel',
            name='lastclean',
            field=models.DateTimeField(default=datetime.datetime(2000, 1, 1, 23, 55, 59, 342380)),
        ),
        migrations.AlterField(
            model_name='tfmodel',
            name='lastfile',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 9, 13, 14, 8, 237710)),
        ),
    ]
