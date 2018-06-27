from logging import getLogger

from datahub.core.exceptions import DataHubException
from datahub.core.utils import slice_iterable_into_chunks
from datahub.search.elasticsearch import bulk

logger = getLogger(__name__)

PROGRESS_INTERVAL = 20000
BULK_INDEX_TIMEOUT_SECS = 300
BULK_DELETION_TIMEOUT_SECS = 300


def sync_app(search_app, batch_size=None):
    """Syncs objects for an app to ElasticSearch in batches of batch_size."""
    model_name = search_app.es_model.__name__
    batch_size = batch_size or search_app.bulk_batch_size
    logger.info(f'Processing {model_name} records, using batch size {batch_size}')

    read_indices, write_index = search_app.es_model.get_read_and_write_indices()
    remove_indices = read_indices - {write_index}

    rows_processed = 0
    total_rows = search_app.queryset.count()
    it = search_app.queryset.iterator(chunk_size=batch_size)
    batches = slice_iterable_into_chunks(it, batch_size)
    for batch in batches:
        actions = list(search_app.es_model.db_objects_to_es_documents(batch, index=write_index))
        num_actions = len(actions)
        bulk(
            actions=actions,
            chunk_size=num_actions,
            request_timeout=BULK_INDEX_TIMEOUT_SECS,
        )

        for index in remove_indices:
            _delete_documents(index, actions)

        emit_progress = (
            (rows_processed + num_actions) // PROGRESS_INTERVAL
            - rows_processed // PROGRESS_INTERVAL
            > 0
        )

        rows_processed += num_actions

        if emit_progress:
            logger.info(f'{model_name} rows processed: {rows_processed}/{total_rows} '
                        f'{rows_processed*100//total_rows}%')

    logger.info(f'{model_name} rows processed: {rows_processed}/{total_rows} 100%.')


def _delete_documents(index, complete_index_actions):
    delete_actions = (
        _create_delete_action(index, action['_type'], action['_id'])
        for action in complete_index_actions
    )

    _, errors = bulk(
        actions=delete_actions,
        chunk_size=len(complete_index_actions),
        request_timeout=BULK_DELETION_TIMEOUT_SECS,
        raise_on_error=False,
    )

    non_404_errors = [error for error in errors if error['delete']['status'] != 404]
    if non_404_errors:
        raise DataHubException(
            f'One or more errors during an Elasticsearch bulk deletion operation: '
            f'{non_404_errors!r}'
        )


def _create_delete_action(_index, _type, _id):
    return {
        '_op_type': 'delete',
        '_index': _index,
        '_type': _type,
        '_id': _id,
    }
