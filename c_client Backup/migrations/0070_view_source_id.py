# Generated by Django 3.1 on 2020-10-25 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0069_auto_20201022_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='view',
            name='source_id',
            field=models.IntegerField(default=0),
        ),
    ]