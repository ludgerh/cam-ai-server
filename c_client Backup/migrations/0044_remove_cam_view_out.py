# Generated by Django 3.1 on 2020-09-30 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0043_cam_view_out'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cam',
            name='view_out',
        ),
    ]