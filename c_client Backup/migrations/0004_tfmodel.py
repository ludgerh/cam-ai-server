# Generated by Django 3.1 on 2020-08-21 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0003_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='tfmodel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('size', models.IntegerField(default=0)),
                ('dir', models.CharField(max_length=256)),
                ('type', models.IntegerField(default=1)),
                ('trigger', models.IntegerField(default=500)),
                ('lastfile', models.DateTimeField()),
                ('lastclean', models.IntegerField(default=0)),
                ('active', models.IntegerField(default=1)),
            ],
        ),
    ]