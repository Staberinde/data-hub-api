# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-21 14:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0010_auto_20170807_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='telephone_number',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
