# Generated by Django 2.2.4 on 2019-11-05 20:18

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('company_list', '0009_remove_list_item_adviser_from_django'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='companylistitem',
                    name='adviser',
                    field=models.ForeignKey(
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        related_name='company_list_items',
                        to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name='companylistitem',
            name='adviser',
        ),
    ]