# Generated by Django 3.1 on 2021-06-24 18:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0111_stream'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventer',
            name='made',
            field=models.DateTimeField(default=datetime.datetime(2021, 6, 24, 18, 35, 32, 658667, tzinfo=utc)),
        ),
    ]