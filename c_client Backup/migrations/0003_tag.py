# Generated by Django 3.1 on 2020-08-21 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0002_auto_20200814_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sorting', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('active', models.IntegerField(default=1)),
            ],
        ),
    ]
