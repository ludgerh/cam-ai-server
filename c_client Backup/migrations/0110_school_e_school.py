# Generated by Django 3.1 on 2021-05-18 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0109_view_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='e_school',
            field=models.IntegerField(default=1),
        ),
    ]