# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-24 18:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0020_auto_20180124_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='nameKey',
            field=models.CharField(default=django.utils.timezone.now, max_length=50, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
