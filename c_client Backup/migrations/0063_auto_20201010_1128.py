# Generated by Django 3.1 on 2020-10-10 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0062_auto_20201010_1052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fit',
            old_name='model',
            new_name='school',
        ),
    ]
