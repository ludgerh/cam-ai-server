# Generated by Django 3.1 on 2021-06-24 18:36

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0113_auto_20210624_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventer',
            name='made',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 24, 18, 36, 56, 240430, tzinfo=utc)),
        ),
    ]
