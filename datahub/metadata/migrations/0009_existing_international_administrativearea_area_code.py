from pathlib import PurePath

from django.db import migrations

from datahub.core.migration_utils import load_yaml_data_in_migration


def load_existing_international_area_codes(apps, schema_editor):
    load_yaml_data_in_migration(
        apps,
        PurePath(__file__).parent / '0009_existing_international_administrativearea_area_code.yaml'
    )


class Migration(migrations.Migration):
    dependencies = [
        ('metadata', '0008_canadian_administrativearea_area_code'),
    ]

    operations = [
        migrations.RunPython(load_existing_international_area_codes, migrations.RunPython.noop),
    ]