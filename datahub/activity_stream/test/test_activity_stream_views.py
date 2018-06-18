import datetime

import mohawk
import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse


def _auth_header(key_id, secret_key, url, method, content, content_type):
    return mohawk.Sender({
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    },
        url,
        method,
        content=content,
        content_type=content_type,
    ).request_header


def _url():
    return 'http://testserver' + reverse('api-v3:activity-stream:index')


def _url_incorrect_domain():
    return 'http://incorrect' + reverse('api-v3:activity-stream:index')


def _url_incorrect_path():
    return 'http://testserver' + reverse('api-v3:activity-stream:index') + 'incorrect/'


@pytest.mark.parametrize(
    'get_kwargs,expected_json',
    (
        (
            # If no X-Forwarded-For header
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret', _url(), 'GET', '', '',
                )
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the first IP in X-Forwarded-For header isn't in the whitelist
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret', _url(), 'GET', '', '',
                ),
                HTTP_X_FORWARDED_FOR='9.9.9.9',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header isn't passed
            dict(
                content_type='',
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Authentication credentials were not provided.'},
        ),
        (
            # If the Authorization header generated from an incorrect ID
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id-incorrect', 'some-secret', _url(), 'GET', '', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect secret
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret-incorrect', _url(), 'GET', '', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect domain
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret',
                    _url_incorrect_domain(), 'GET', '', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect path
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret',
                    _url_incorrect_path(), 'GET', '', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect method
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret',
                    _url_incorrect_path(), 'POST', '', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect content-type
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret',
                    _url_incorrect_path(), 'GET', 'incorrect', '',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from incorrect content
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_header(
                    'some-id', 'some-secret',
                    _url_incorrect_path(), 'GET', '', 'incorrect',
                ),
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
    ),
)
@pytest.mark.django_db
def test_401_returned(api_client, get_kwargs, expected_json):
    """If the request isn't properly Hawk-authenticated, then a 401 is returned"""
    response = api_client.get(
        _url(),
        **get_kwargs,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_json


@pytest.mark.django_db
def test_if_authentication_passed_but_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() + datetime.timedelta(seconds=-61)
    with freeze_time(past):
        auth = _auth_header(
            'some-id', 'some-secret', _url(), 'GET', '', '',
        )
    response = api_client.get(
        reverse('api-v3:activity-stream:index'),
        content_type='',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error


@pytest.mark.usefixtures('local_memory_cache')
@pytest.mark.django_db
def test_if_authentication_reused_401_returned(api_client):
    """If the Authorization header is reused, then a 401 is returned"""
    auth = _auth_header(
        'some-id', 'some-secret', _url(), 'GET', '', '',
    )

    response_1 = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4',
    )
    assert response_1.status_code == status.HTTP_200_OK

    response_2 = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4',
    )
    assert response_2.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response_2.json() == error


@pytest.mark.django_db
def test_empty_object_returned(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct data is retuend
    """
    auth = _auth_header(
        'some-id', 'some-secret', _url(), 'GET', '', ''
    )
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4',
    )

    assert response.status_code == status.HTTP_200_OK
    content = {'secret': 'content-for-pen-test'}
    assert response.json() == content
