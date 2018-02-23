# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-29 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0007_add_date_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='kind',
            field=models.CharField(choices=[
                ('interaction', 'Interaction'),
                ('service_delivery', 'Service delivery'),
                ('policy', 'Policy interaction'),
            ], default='interaction', max_length=255),
            preserve_default=False,
        ),
    ]
