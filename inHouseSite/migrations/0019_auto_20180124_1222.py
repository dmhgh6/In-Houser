# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-24 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0018_auto_20180124_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='player',
            name='steamId',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
