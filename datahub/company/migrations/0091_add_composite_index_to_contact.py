# Generated by Django 2.2.5 on 2019-09-23 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0090_add_company_dnb_investigation_data'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['created_on', 'id'], name='company_con_created_dbaf20_idx'),
        ),
    ]