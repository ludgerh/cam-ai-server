# Generated by Django 3.1 on 2021-01-19 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_client', '0087_event_done'),
    ]

    operations = [
        migrations.CreateModel(
            name='videoclip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='videoclips',
            field=models.ManyToManyField(to='c_client.videoclip'),
        ),
    ]
