# Generated by Django 3.1 on 2020-12-02 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0076_auto_20201129_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cam',
            name='school',
        ),
        migrations.RemoveField(
            model_name='detector',
            name='school',
        ),
        migrations.RemoveField(
            model_name='view',
            name='school',
        ),
    ]