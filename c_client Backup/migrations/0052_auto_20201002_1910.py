# Generated by Django 3.1 on 2020-10-02 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0051_auto_20201002_1907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cam',
            name='running',
        ),
        migrations.RemoveField(
            model_name='cam',
            name='source_nr',
        ),
        migrations.RemoveField(
            model_name='cam',
            name='source_type',
        ),
        migrations.RemoveField(
            model_name='view',
            name='running',
        ),
        migrations.RemoveField(
            model_name='view',
            name='source_nr',
        ),
        migrations.RemoveField(
            model_name='view',
            name='source_type',
        ),
    ]
