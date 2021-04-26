# Generated by Django 3.1.8 on 2021-04-23 17:00

import datahub.core.validators.telephone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_flag', '0003_populate_personalised_dashboard_user_feature_flag'),
        ('company', '0110_advisor_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='features',
            field=models.ManyToManyField(blank=True, help_text="User's feature flags. Note that the feature flag also needs to be set to active.", related_name='advisers', to='feature_flag.UserFeatureFlag'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='telephone_alternative',
            field=models.CharField(blank=True, null=True, default='', max_length=255, validators=[datahub.core.validators.telephone.InternationalTelephoneValidator()]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='telephone_countrycode',
            field=models.CharField(max_length=255, validators=[datahub.core.validators.telephone.TelephoneCountryCodeValidator()]),
        ),
        migrations.AlterField(
            model_name='contact',
            name='telephone_number',
            field=models.CharField(max_length=255, validators=[datahub.core.validators.telephone.TelephoneValidator()]),
        ),
    ]
