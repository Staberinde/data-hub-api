from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import HTTPError, Timeout

from datahub.core.api_client import APIClient, HawkAuth
from datahub.core.exceptions import APIBadGatewayException


class CompanyMatchingServiceError(Exception):
    """
    Base exception class for Company matching service related errors.
    """


class CompanyMatchingServiceHTTPError(CompanyMatchingServiceError):
    """
    Exception for when Company matching service returns an http error status.
    """


class CompanyMatchingServiceTimeoutError(CompanyMatchingServiceError):
    """
    Exception for when a timeout was encountered when connecting to Company matching service.
    """


class CompanyMatchingServiceConnectionError(CompanyMatchingServiceError):
    """
    Exception for when an error was encountered when connecting to Company matching service.
    """


def request_match_companies(json_body, request=None):
    """
    Queries the company matching service with the given json_body. E.g.:
    {
        "descriptions": [
            {
                "id": "1",
                "companies_house_id": "0921309",
                "duns_number": "d210"
                "company_name":"apple",
                "contact_email": "john@apple.com",
                "cdms_ref": "782934",
                "postcode": "SW129RP"
            }
        ]
    }

    Note that the ID field typically the company UUID that is returned by the api for data mapping.
    ID and at least one of the following fields companies_house_id, duns_number, company_name,
    contact_email, cdms_ref and postcode are required.
    """
    if not all([
        settings.COMPANY_MATCHING_SERVICE_BASE_URL,
        settings.COMPANY_MATCHING_HAWK_ID,
        settings.COMPANY_MATCHING_HAWK_KEY,
    ]):
        raise ImproperlyConfigured('The all COMPANY_MATCHING_SERVICE_* setting must be set')

    api_client = APIClient(
        api_url=settings.COMPANY_MATCHING_SERVICE_BASE_URL,
        auth=HawkAuth(settings.COMPANY_MATCHING_HAWK_ID,
                      settings.COMPANY_MATCHING_HAWK_KEY),
        raise_for_status=True,
        default_timeout=settings.DEFAULT_SERVICE_TIMEOUT,
        request=request,
    )
    return api_client.request(
        'POST',
        'api/v1/company/match/',
        json=json_body,
        timeout=3.0,
    )


def _format_company_for_post(companies):
    """Format the Company model to json for the POST body."""
    descriptions = [
        {
            'id': str(company.id),
            'company_name': company.name,
            'companies_house_id': company.company_number,
            'duns_number': company.duns_number,
            'postcode': company.address_postcode,
            'cdms_ref': company.reference_code,
        }
        for company in companies
    ]

    return {
        'descriptions': [
            {
                key: value
                for key, value in description.items() if value
            }
            for description in descriptions
        ],
    }


def match_company(companies, request=None):
    """
    Get match id for all Company objects and return response from the company
    matching service.
    Raises exception an requests.exceptions.HTTPError for status, timeout and a connection error.
    """
    try:
        response = request_match_companies(
            _format_company_for_post(companies),
            request,
        )
    except APIBadGatewayException as exc:
        error_message = 'Encountered an error connecting to Company matching service'
        raise CompanyMatchingServiceConnectionError(error_message) from exc
    except Timeout as exc:
        error_message = 'Encountered a timeout interacting with Company matching service'
        raise CompanyMatchingServiceTimeoutError(error_message) from exc
    except HTTPError as exc:
        error_message = (
            'The Company matching service returned an error status: '
            f'{exc.response.status_code}',
        )
        raise CompanyMatchingServiceHTTPError(error_message) from exc
    return response
