# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-13 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_appcustomization_custom_helpdesk_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appcustomization',
            name='custom_helpdesk_link',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
