# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 16:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omis_payment', '0002_auto_20171011_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='received_on',
            field=models.DateField(),
        ),
    ]
