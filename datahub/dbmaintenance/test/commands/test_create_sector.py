from io import BytesIO

import factory
import pytest
from django.core.management import call_command
from reversion.models import Version

from datahub.metadata.models import Sector
from datahub.metadata.test.factories import SectorClusterFactory, SectorFactory

pytestmark = pytest.mark.django_db


def test_happy_path(s3_stubber):
    """Test that the command creates the specified records."""
    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},{clusters[2]},{parent_sector.pk}
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key)

    sectors = Sector.objects.filter(pk__in=sector_pks)
    assert [str(sectors[0].pk), str(sectors[1].pk), str(sectors[2].pk)] == sector_pks
    assert [sectors[0].segment, sectors[1].segment, sectors[2].segment] == segments
    assert [
        sectors[0].sector_cluster.name,
        sectors[1].sector_cluster.name,
        sectors[2].sector_cluster.name,
    ] == clusters
    assert [
        sectors[0].parent,
        sectors[1].parent,
        sectors[2].parent,
    ] == [parent_sector, parent_sector, parent_sector]


def test_blank_parent(s3_stubber):
    """Test that the command creates the specified records when no parent is provided."""
    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},{clusters[2]},
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key)

    sectors = Sector.objects.filter(pk__in=sector_pks)
    assert [str(sectors[0].pk), str(sectors[1].pk), str(sectors[2].pk)] == sector_pks
    assert [sectors[0].segment, sectors[1].segment, sectors[2].segment] == segments
    assert [
        sectors[0].sector_cluster.name,
        sectors[1].sector_cluster.name,
        sectors[2].sector_cluster.name,
    ] == clusters
    assert [
        sectors[0].parent,
        sectors[1].parent,
        sectors[2].parent,
    ] == [parent_sector, parent_sector, None]


def test_blank_sector_cluster(s3_stubber):
    """Test that the command creates the specified records when no sector cluster is provided."""
    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},,{parent_sector.pk}
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key)

    sectors = Sector.objects.filter(pk__in=sector_pks)
    assert [str(sectors[0].pk), str(sectors[1].pk), str(sectors[2].pk)] == sector_pks
    assert [sectors[0].segment, sectors[1].segment, sectors[2].segment] == segments
    assert [sectors[0].sector_cluster.name, sectors[1].sector_cluster.name] == clusters[:2]
    assert not sectors[2].sector_cluster
    assert [
        sectors[0].parent,
        sectors[1].parent,
        sectors[2].parent,
    ] == [parent_sector, parent_sector, parent_sector]


def test_non_existent_parent(s3_stubber, caplog):
    """Test that the command logs an error when parent PK does not exist."""
    caplog.set_level('ERROR')

    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},{clusters[2]},00000000-0000-0000-0000-000000000000
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key)

    sectors = Sector.objects.filter(pk__in=sector_pks)

    assert 'Sector matching query does not exist' in caplog.text
    assert len(caplog.records) == 1

    assert [str(sectors[0].pk), str(sectors[1].pk)] == sector_pks[:2]
    assert [sectors[0].segment, sectors[1].segment] == segments[:2]
    assert [sectors[0].sector_cluster.name, sectors[1].sector_cluster.name] == clusters[:2]


def test_simulate(s3_stubber):
    """Test that the command simulates creations if --simulate is passed in."""
    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},{clusters[2]},{parent_sector.pk}
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key, simulate=True)

    sectors = Sector.objects.filter(pk__in=sector_pks)
    assert not sectors


def test_audit_log(s3_stubber):
    """Test that reversion revisions are created."""
    sector_pks = [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003',
    ]
    segments = ['segment_1', 'segment_2', 'segment_3']
    clusters = ['cluster_1', 'cluster_2', 'cluster_3']
    SectorClusterFactory.create_batch(
        3,
        name=factory.Iterator(clusters),
    )
    parent_sector = SectorFactory()

    bucket = 'test_bucket'
    object_key = 'test_key'
    csv_content = f"""id,segment,sector_cluster,parent_id
{sector_pks[0]},{segments[0]},{clusters[0]},{parent_sector.pk}
{sector_pks[1]},{segments[1]},{clusters[1]},{parent_sector.pk}
{sector_pks[2]},{segments[2]},{clusters[2]},{parent_sector.pk}
"""

    s3_stubber.add_response(
        'get_object',
        {
            'Body': BytesIO(csv_content.encode(encoding='utf-8')),
        },
        expected_params={
            'Bucket': bucket,
            'Key': object_key,
        },
    )

    call_command('create_sector', bucket, object_key)

    sectors = Sector.objects.filter(pk__in=sector_pks)

    for sector in sectors:
        versions = Version.objects.get_for_object(sector)
        assert versions.count() == 1
        assert versions[0].revision.get_comment() == 'Sector creation.'
