# Generated by Django 3.0.6 on 2020-05-19 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_list', '0015_auto_20200519_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineitem',
            name='name',
            field=models.CharField(
                blank=True,
                help_text='Name to represent the item within the pipeline',
                max_length=255
            ),
        ),
    ]