# Generated by Django 3.1 on 2021-01-23 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0090_auto_20210123_1948'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='videoclips',
            new_name='videoclip',
        ),
    ]