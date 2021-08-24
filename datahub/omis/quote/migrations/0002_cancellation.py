# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-04 11:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('omis_quote', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='cancelled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quote',
            name='cancelled_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
