# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-18 22:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0007_auto_20180118_1522'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='season',
            name='gameEight',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameFive',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameFour',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameOne',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameSeven',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameSix',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameThree',
        ),
        migrations.RemoveField(
            model_name='season',
            name='gameTwo',
        ),
        migrations.AddField(
            model_name='game',
            name='gameNumber',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='seasonNumber',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Season',
        ),
    ]
