# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-24 16:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0015_auto_20180124_1032'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GameModel',
            new_name='Game',
        ),
    ]