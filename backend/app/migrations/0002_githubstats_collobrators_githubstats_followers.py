# Generated by Django 5.1.4 on 2024-12-31 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='githubstats',
            name='collobrators',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='githubstats',
            name='followers',
            field=models.IntegerField(default=0),
        ),
    ]
