# Generated by Django 3.1 on 2020-10-02 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0050_auto_20201002_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='cam',
            name='source_nr',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cam',
            name='source_type',
            field=models.CharField(default='X', max_length=1),
        ),
    ]
