# Generated by Django 3.1 on 2020-09-23 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0033_auto_20200923_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='cam',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cam',
            name='running',
            field=models.BooleanField(default=False),
        ),
    ]