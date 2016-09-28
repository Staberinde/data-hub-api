# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-28 13:21
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_auto_20160921_1417'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advisor',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='businesstype',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='employeerange',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='interactiontype',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='sector',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='turnoverrange',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='ukregion',
            options={'ordering': ('name',)},
        ),
        migrations.RemoveField(
            model_name='company',
            name='uk_based',
        ),
        migrations.AlterField(
            model_name='advisor',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='country',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='employeerange',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='interactiontype',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='role',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sector',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='title',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='turnoverrange',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ukregion',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
    ]
