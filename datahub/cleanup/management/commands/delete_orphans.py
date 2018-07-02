from datetime import timedelta
from logging import getLogger
from secrets import token_urlsafe

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from django.template.defaultfilters import capfirst
from django.utils.timezone import now

from datahub.cleanup.cleanup_config import (
    CleanupConfig,
    CleanupType,
    get_config_for_type_and_model,
    get_configs_for_type,
    register_config,
)
from datahub.company.models import Company, Contact
from datahub.event.models import Event


logger = getLogger(__name__)


@register_config(CleanupType.orphaned, Contact)
class OrphanedContactCleanupConfig(CleanupConfig):
    """Deletion configuration for orphaned contacts."""


@register_config(CleanupType.orphaned, Company)
class OrphanedCompanyCleanupConfig(CleanupConfig):
    """Deletion configuration for orphaned company."""


@register_config(CleanupType.orphaned, Event)
class OrphanedEventCleanupConfig(CleanupConfig):
    """Deletion configuration for orphaned events."""

    date_field = 'end_date'


def get_related_fields(model):
    """
    Returns all the fields of `model` that hold the link between referencing objects
    and the referenced object (`model`).

    :param model: orphaned model class
    :returns: list of fields of `model` that hold references via dependent objects
    """
    return [
        f for f in model._meta.get_fields(include_hidden=True)
        if (f.one_to_many or f.one_to_one or f.many_to_many or f.many_to_one)
        and f.auto_created
        and not f.concrete
        and not f.field.model._meta.auto_created
    ]


def get_unreferenced_objects_query(model):
    """
    :param model: orphaned model class
    :returns: queryset for unreferenced objects
    """
    fields = get_related_fields(model)

    identifiers = [f'ann_{token_urlsafe(6)}' for _ in range(len(fields))]

    qs = model.objects.all()
    for identifier, field in zip(identifiers, fields):
        related_field = field.field
        subquery = related_field.model.objects.filter(
            **{related_field.attname: OuterRef('pk')},
        ).only('pk')
        qs = qs.annotate(**{identifier: Exists(subquery)})

    filter_args = {identifier: False for identifier in identifiers}

    return qs.filter(**filter_args)


class Command(BaseCommand):
    """
    Django command to delete orphaned records for `model`.
    Orphans are `days_before_orphaning` old records without any objects referencing them.

    If the argument `simulate=True` is passed in, the command only simulates the action.
    """

    def add_arguments(self, parser):
        """Define extra arguments."""
        parser.add_argument(
            'model',
            choices=[model._meta.label for model in get_configs_for_type(CleanupType.orphaned)],
            help='Model to clean up.',
        )
        parser.add_argument(
            '--simulate',
            action='store_true',
            default=False,
            help='If True it only simulates the command and prints the SQL query.',
        )

    def handle(self, *args, **options):
        """Main logic for the actual command."""
        model = apps.get_model(options['model'])
        config = get_config_for_type_and_model(CleanupType.orphaned, model)

        qs = get_unreferenced_objects_query(model)
        qs = qs.filter(
            **{f'{config.date_field}__lt': now() - timedelta(config.age_threshold)}
        ).order_by('-modified_on')

        model_verbose_name = capfirst(model._meta.verbose_name_plural)
        logger.info(f'{model_verbose_name} to delete: {qs.count()}')

        if options['simulate']:
            logger.info(f'SQL:\n{qs.query}')
        else:
            deleted = qs.delete()
            logger.info(f'{model_verbose_name} deleted: {deleted}')
