# Generated by Django 3.1 on 2020-10-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0065_userinfo_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='epoch',
            name='hit100',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='epoch',
            name='val_hit100',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='fit',
            name='hit100',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='fit',
            name='val_hit100',
            field=models.FloatField(default=0),
        ),
    ]