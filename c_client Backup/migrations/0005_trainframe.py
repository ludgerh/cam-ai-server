# Generated by Django 3.1 on 2020-08-25 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0004_tfmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='trainframe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('made', models.DateTimeField()),
                ('to_go', models.SmallIntegerField()),
                ('name', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=2)),
                ('c0', models.SmallIntegerField()),
                ('c1', models.SmallIntegerField()),
                ('c2', models.SmallIntegerField()),
                ('c3', models.SmallIntegerField()),
                ('c4', models.SmallIntegerField()),
                ('c5', models.SmallIntegerField()),
                ('c6', models.SmallIntegerField()),
                ('c7', models.SmallIntegerField()),
                ('c8', models.SmallIntegerField()),
                ('c9', models.SmallIntegerField()),
                ('weight', models.FloatField()),
                ('checked', models.SmallIntegerField()),
            ],
        ),
    ]