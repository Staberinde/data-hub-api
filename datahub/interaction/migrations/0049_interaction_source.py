# Generated by Django 2.2 on 2019-04-17 11:03

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0048_add_archive_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='interaction',
            name='source',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]