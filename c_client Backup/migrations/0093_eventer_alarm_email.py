# Generated by Django 3.1 on 2021-01-29 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0092_event_double'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventer',
            name='alarm_email',
            field=models.CharField(default='', max_length=255, verbose_name='alarm email'),
        ),
    ]
