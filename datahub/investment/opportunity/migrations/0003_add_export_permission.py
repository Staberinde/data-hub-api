# Generated by Django 3.1.7 on 2021-04-09 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opportunity', '0002_auto_20210222_1025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='largecapitalopportunity',
            options={'permissions': (('export_largecapitalopportunity', 'Can export large capital opportunity'),), 'verbose_name_plural': 'large capital opportunities'},
        ),
    ]
