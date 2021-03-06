# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-18 21:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inHouseSite', '0006_remove_document_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seasonNumber', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='game',
            name='date',
        ),
        migrations.AddField(
            model_name='season',
            name='gameEight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameEight', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameFive',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameFive', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameFour',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameFour', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameOne',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameOne', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameSeven',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameSeven', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameSix',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameSix', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameThree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameThree', to='inHouseSite.Game'),
        ),
        migrations.AddField(
            model_name='season',
            name='gameTwo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='GameTwo', to='inHouseSite.Game'),
        ),
    ]
