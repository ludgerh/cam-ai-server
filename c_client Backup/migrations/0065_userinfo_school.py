# Generated by Django 3.1 on 2020-10-10 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0064_auto_20201010_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='c_client.school'),
        ),
    ]