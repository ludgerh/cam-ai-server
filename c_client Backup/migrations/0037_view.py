# Generated by Django 3.1 on 2020-09-26 14:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0036_cam_feed_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='view',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('made', models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0))),
                ('lastused', models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0))),
                ('xres', models.IntegerField(default=0)),
                ('yres', models.IntegerField(default=0)),
                ('fpslimit', models.FloatField(default=0)),
                ('fpsactual', models.FloatField(default=0)),
                ('running', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
