# Generated by Django 3.1 on 2020-11-16 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0073_auto_20201116_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='mask',
            name='cam',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='c_client.cam'),
        ),
    ]
