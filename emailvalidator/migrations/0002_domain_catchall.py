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
            field=models.CharField(blank=True, null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='EmailRegExValidator',
            name='allow_all',
            field=models.BooleanField(blank=True, null=True, default=False),
        ),
    ]
