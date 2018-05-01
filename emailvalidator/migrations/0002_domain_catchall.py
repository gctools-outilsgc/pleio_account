# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-06 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailvalidator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='EmailRegExValidator',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='EmailRegExValidator',
            name='allow_all',
            field=models.BooleanField(default=False, verbose_name='Allow all from domain'),
        ),
    ]
