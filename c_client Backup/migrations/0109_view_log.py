# Generated by Django 3.1 on 2021-04-06 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0108_auto_20210323_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='view_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('v_type', models.CharField(max_length=1)),
                ('v_id', models.IntegerField()),
                ('start', models.DateTimeField()),
                ('stop', models.DateTimeField()),
                ('user', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]