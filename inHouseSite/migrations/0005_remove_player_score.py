# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-29 18:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0004_remove_player_isbot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='score',
        ),
    ]
