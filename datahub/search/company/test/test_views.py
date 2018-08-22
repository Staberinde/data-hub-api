import random
from cgi import parse_header
from collections import Counter
from csv import DictReader
from io import StringIO
from unittest import mock
from uuid import UUID, uuid4

import factory
import pytest
from django.conf import settings
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.company.constants import BusinessTypeConstant
from datahub.company.models import Company, CompanyPermission
from datahub.company.test.factories import (
    AdviserFactory,
    CompaniesHouseCompanyFactory,
    CompanyFactory,
    ContactFactory
)
from datahub.core import constants
from datahub.core.test_utils import (
    APITestMixin,
    create_test_user,
    format_csv_data,
    get_attr_or_none,
    random_obj_for_model,
    random_obj_for_queryset,
)
from datahub.metadata.models import CompanyClassification, Sector
from datahub.metadata.test.factories import TeamFactory
from datahub.search.company.views import SearchCompanyExportAPIView

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup_data(setup_es):
    """Sets up data for the tests."""
    country_uk = constants.Country.united_kingdom.value.id
    country_us = constants.Country.united_states.value.id
    uk_region = constants.UKRegion.south_east.value.id
    CompanyFactory(
        name='abc defg ltd',
        trading_address_1='1 Fake Lane',
        trading_address_town='Downtown',
        trading_address_country_id=country_uk,
        uk_region_id=uk_region,
    )
    CompanyFactory(
        name='abc defg us ltd',
        trading_address_1='1 Fake Lane',
        trading_address_town='Downtown',
        trading_address_country_id=country_us,
        registered_address_country_id=country_us
    )
    setup_es.indices.refresh()


@pytest.fixture
def setup_headquarters_data(setup_es):
    """Sets up data for headquarter type tests."""
    CompanyFactory(
        name='ghq',
        headquarter_type_id=constants.HeadquarterType.ghq.value.id,
    )
    CompanyFactory(
        name='ehq',
        headquarter_type_id=constants.HeadquarterType.ehq.value.id,
    )
    CompanyFactory(
        name='ukhq',
        headquarter_type_id=constants.HeadquarterType.ukhq.value.id,
    )
    CompanyFactory(
        name='none',
        headquarter_type_id=None,
    )
    setup_es.indices.refresh()


class TestSearch(APITestMixin):
    """Tests search views."""

    def test_company_search_no_permissions(self):
        """Should return 403"""
        user = create_test_user(dit_team=TeamFactory())
        api_client = self.create_api_client(user=user)
        url = reverse('api-v3:search:company')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'archived', (
            True,
            False,
        )
    )
    def test_archived_filter(self, setup_es, archived):
        """Tests filtering by archived."""
        matching_companies = CompanyFactory.create_batch(5, archived=archived)
        CompanyFactory.create_batch(2, archived=not archived)

        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'archived': archived,
        })

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['count'] == 5

        expected_ids = Counter(str(company.pk) for company in matching_companies)
        actual_ids = Counter(result['id'] for result in response_data['results'])
        assert expected_ids == actual_ids

    def test_trading_address_country_filter(self, setup_data):
        """Tests trading address country filter."""
        url = reverse('api-v3:search:company')
        united_states_id = constants.Country.united_states.value.id

        response = self.api_client.post(url, {
            'trading_address_country': united_states_id,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['trading_address_country']['id'] == united_states_id

    def test_uk_region_filter(self, setup_data):
        """Tests uk region filter."""
        url = reverse('api-v3:search:company')
        uk_region = constants.UKRegion.south_east.value.id

        response = self.api_client.post(url, {
            'uk_region': uk_region,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['uk_region']['id'] == uk_region

    @pytest.mark.parametrize(
        'query,results', (
            (
                {
                    'headquarter_type': None,
                },
                {'none'},
            ),
            (
                {
                    'headquarter_type': constants.HeadquarterType.ghq.value.id
                },
                {'ghq'},
            ),
            (
                {
                    'headquarter_type': [
                        constants.HeadquarterType.ghq.value.id,
                        constants.HeadquarterType.ehq.value.id,
                    ],
                },
                {'ehq', 'ghq'},
            ),
            (
                {
                    'headquarter_type': [
                        constants.HeadquarterType.ghq.value.id,
                        constants.HeadquarterType.ehq.value.id,
                        None,
                    ],
                },
                {'ehq', 'ghq', 'none'},
            ),
        )
    )
    def test_headquarter_type_filter(self, setup_headquarters_data, query, results):
        """Test headquarter type filter."""
        url = reverse('api-v3:search:company')
        response = self.api_client.post(
            url,
            query,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

        num_results = len(results)
        assert response.data['count'] == num_results
        assert len(response.data['results']) == num_results

        search_results = {company['name'] for company in response.data['results']}
        assert search_results == results

    def test_global_headquarters(self, setup_es):
        """Test global headquarters filter."""
        ghq1 = CompanyFactory(headquarter_type_id=constants.HeadquarterType.ghq.value.id)
        ghq2 = CompanyFactory(headquarter_type_id=constants.HeadquarterType.ghq.value.id)
        companies = CompanyFactory.create_batch(5, global_headquarters=ghq1)
        CompanyFactory.create_batch(5, global_headquarters=ghq2)
        CompanyFactory.create_batch(10)

        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')
        response = self.api_client.post(
            url,
            {
                'global_headquarters': ghq1.id
            }
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data['count'] == 5
        assert len(response.data['results']) == 5

        search_results = {UUID(company['id']) for company in response.data['results']}
        assert search_results == {company.id for company in companies}

    @pytest.mark.parametrize(
        'sector_level',
        (0, 1, 2),
    )
    def test_sector_descends_filter(self, hierarchical_sectors, setup_es, sector_level):
        """Test the sector_descends filter."""
        num_sectors = len(hierarchical_sectors)
        sectors_ids = [sector.pk for sector in hierarchical_sectors]

        companies = CompanyFactory.create_batch(
            num_sectors,
            sector_id=factory.Iterator(sectors_ids)
        )
        CompanyFactory.create_batch(
            3,
            sector=factory.LazyFunction(lambda: random_obj_for_queryset(
                Sector.objects.exclude(pk__in=sectors_ids)
            ))
        )

        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')
        body = {
            'sector_descends': hierarchical_sectors[sector_level].pk
        }
        response = self.api_client.post(url, body)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data['count'] == num_sectors - sector_level

        actual_ids = {UUID(company['id']) for company in response_data['results']}
        expected_ids = {company.pk for company in companies[sector_level:]}
        assert actual_ids == expected_ids

    @pytest.mark.parametrize(
        'country,match',
        (
            (constants.Country.cayman_islands.value.id, True),
            (constants.Country.montserrat.value.id, True),
            (constants.Country.st_helena.value.id, False),
            (constants.Country.anguilla.value.id, False),
        )
    )
    def test_composite_country_filter(self, setup_es, country, match):
        """Tests composite country filter."""
        company = CompanyFactory(
            trading_address_country_id=constants.Country.cayman_islands.value.id,
            registered_address_country_id=constants.Country.montserrat.value.id,
        )
        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'country': country,
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        if match:
            assert response.data['count'] == 1
            assert len(response.data['results']) == 1
            assert response.data['results'][0]['id'] == str(company.id)
        else:
            assert response.data['count'] == 0
            assert len(response.data['results']) == 0

    @pytest.mark.parametrize(
        'name,match',
        (
            ('whiskers', True),
            ('house lion', True),
            ('tiger', False),
            ('panda', False),
        )
    )
    def test_composite_name_filter(self, setup_es, name, match):
        """Tests composite name filter."""
        company = CompanyFactory(
            name='whiskers and tabby',
            alias='house lion and moggie',
        )
        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'name': name,
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        if match:
            assert response.data['count'] == 1
            assert len(response.data['results']) == 1
            assert response.data['results'][0]['id'] == str(company.id)
        else:
            assert response.data['count'] == 0
            assert len(response.data['results']) == 0

    def test_multiple_trading_address_country_filter(self, setup_data):
        """Tests multiple trading address countries filter."""
        term = 'abc defg'

        url = reverse('api-v3:search:company')
        united_states_id = constants.Country.united_states.value.id
        united_kingdom_id = constants.Country.united_kingdom.value.id

        response = self.api_client.post(url, {
            'original_query': term,
            'trading_address_country': [united_states_id, united_kingdom_id],
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        country_ids = {result['trading_address_country']['id']
                       for result in response.data['results']}
        assert country_ids == {united_kingdom_id, united_states_id}

    @pytest.mark.parametrize(
        'company_name,search_name,match',
        (
            ('abcdefghijk', 'abc', True),
            ('abcdefghijk', 'bcd', True),
            ('abcdefghijk', 'hij', True),
            ('abcdefghijk', 'cdefgh', True),
            ('abcdefghijk', 'bcde', True),
            ('abcdefghijk', 'hijk', True),
            ('abcdefghijk', 'abcdefghijk', True),
            ('abcdefghijk', 'abc xyz', False),
            ('abcdefghijk', 'ab', False),
            ('abcdefghijk', 'cats', False),
            ('abcdefghijk', 'xyz', False),
            ('abcdefghijk', 'abd', False),
            ('abcdefghijk', 'abdeghk', False),
            ('abcdefghijk', 'abdeklx', False),
            ('abcdefghijk', 'abcfgzghijk', False),
            ('Pallas Hiding', 'pallas', True),
            ('Pallas Hiding', 'hid', True),
            ('Pallas Hiding', 'las', True),
            ('Pallas Hiding', 'Pallas Hiding', True),
            ('Pallas Hiding', 'Pallas Hid', True),
            ('Pallas Hiding', 'Pallas Hi', True),
            ('A & B', 'A & B', True),
            ('A&B Properties Limited', 'a&b', True)
        )
    )
    def test_name_filter_match(self, setup_es, company_name, search_name, match):
        """Tests company name partial search."""
        company = CompanyFactory(
            name=company_name
        )
        setup_es.indices.refresh()

        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'name': search_name,
        })
        assert response.status_code == status.HTTP_200_OK

        if match:
            assert response.data['count'] == 1
            assert len(response.data['results']) == 1
            assert response.data['results'][0]['id'] == str(company.id)
            assert response.data['results'][0]['name'] == company.name
        else:
            assert response.data['count'] == 0
            assert len(response.data['results']) == 0

    def test_null_filter(self, setup_es):
        """Tests filter with null value."""
        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'uk_region': None,
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'uk_region': ['This field may not be null.']}

    @pytest.mark.parametrize('sortby', (
        {},
        {'sortby': 'name:asc'},
        {'sortby': 'created_on:asc'},
    ))
    def test_company_search_paging(self, setup_es, sortby):
        """Tests if content placement is consistent between pages."""
        ids = sorted((uuid4() for _ in range(9)))

        name = 'test record'

        CompanyFactory.create_batch(
            len(ids),
            id=factory.Iterator(ids),
            name=name,
            alias='',
        )

        setup_es.indices.refresh()

        page_size = 2

        for page in range((len(ids) + page_size - 1) // page_size):
            url = reverse('api-v3:search:company')
            response = self.api_client.post(url, {
                'original_query': name,
                'entity': 'company',
                'offset': page * page_size,
                'limit': page_size,
                **sortby
            })

            assert response.status_code == status.HTTP_200_OK

            start = page * page_size
            end = start + page_size
            assert ids[start:end] == [UUID(company['id']) for company in response.data['results']]

    def test_company_search_paging_query_params(self, setup_data):
        """Tests pagination of results."""
        url = f"{reverse('api-v3:search:company')}?offset=1&limit=1"
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] > 1
        assert len(response.data['results']) == 1

    @mock.patch('datahub.search.query_builder._add_aggs_to_query')
    def test_company_search_no_aggregations(self, _add_aggs_to_query, setup_data):
        """Tests if no aggregation occurs."""
        url = reverse('api-v3:search:company')
        response = self.api_client.post(url)

        assert _add_aggs_to_query.call_count == 0

        assert response.status_code == status.HTTP_200_OK
        assert 'aggregations' not in response.data

    def test_search_company_no_filters(self, setup_data):
        """Tests case where there is no filters provided."""
        url = reverse('api-v3:search:company')
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0

    def test_search_foreign_company_json(self, setup_data):
        """Tests detailed company search."""
        url = reverse('api-v3:search:company')

        response = self.api_client.post(url, {
            'uk_based': False,
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['uk_based'] is False


class TestCompanyExportView(APITestMixin):
    """Tests the company export view."""

    @pytest.mark.parametrize(
        'permissions', (
            (),
            (CompanyPermission.view_company,),
            (CompanyPermission.export_company,),
        )
    )
    def test_user_without_permission_cannot_export(self, setup_es, permissions):
        """Test that a user without the correct permissions cannot export data."""
        user = create_test_user(dit_team=TeamFactory(), permission_codenames=permissions)
        api_client = self.create_api_client(user=user)

        url = reverse('api-v3:search:company-export')
        response = api_client.post(url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'request_sortby,orm_ordering',
        (
            ('name', 'name'),
            ('modified_on', 'modified_on'),
            ('modified_on:desc', '-modified_on'),
        )
    )
    def test_export(
        self,
        setup_es,
        request_sortby,
        orm_ordering,
    ):
        """Test export of company search results."""
        CompanyFactory.create_batch(3)
        CompanyFactory.create_batch(2, hq=True)

        setup_es.indices.refresh()

        data = {}
        if request_sortby:
            data['sortby'] = request_sortby

        url = reverse('api-v3:search:company-export')

        with freeze_time('2018-01-01 11:12:13'):
            response = self.api_client.post(url, format='json', data=data)

        assert response.status_code == status.HTTP_200_OK
        assert parse_header(response.get('Content-Type')) == ('text/csv', {'charset': 'utf-8'})
        assert parse_header(response.get('Content-Disposition')) == (
            'attachment', {'filename': 'Data Hub - Companies - 2018-01-01-11-12-13.csv'}
        )

        sorted_company = Company.objects.order_by(orm_ordering)
        reader = DictReader(StringIO(response.getvalue().decode('utf-8-sig')))

        assert reader.fieldnames == list(SearchCompanyExportAPIView.field_titles.values())

        expected_row_data = [
            {
                'Name': company.name,
                'Link': f'{settings.DATAHUB_FRONTEND_URL_PREFIXES["company"]}/{company.pk}',
                'Sector': get_attr_or_none(company, 'sector.name'),
                'Country': get_attr_or_none(company, 'registered_address_country.name'),
                'UK region': get_attr_or_none(company, 'uk_region.name'),
                'Archived': company.archived,
                'Date created': company.created_on,
                'Number of employees': get_attr_or_none(company, 'employee_range.name'),
                'Annual turnover': get_attr_or_none(company, 'turnover_range.name'),
                'Headquarter type': get_attr_or_none(company, 'headquarter_type.name'),
            }
            for company in sorted_company
        ]

        assert list(dict(row) for row in reader) == format_csv_data(expected_row_data)


class TestBasicSearch(APITestMixin):
    """Tests basic search view."""

    def test_all_companies(self, setup_data):
        """Tests basic aggregate all companies query."""
        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': '',
            'entity': 'company'
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] > 0

    def test_companies(self, setup_data):
        """Tests basic aggregate companies query."""
        term = 'abc defg'

        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': term,
            'entity': 'company'
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['results'][0]['name'].startswith(term)
        assert [{'count': 2, 'entity': 'company'}] == response.data['aggregations']

    def test_search_in_trading_name(self, setup_es):
        """Tests basic aggregate companies query."""
        term = 'NameFiveBiggestWildCats'
        CompanyFactory(alias=term)
        setup_es.indices.refresh()

        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': term,
            'entity': 'company'
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['trading_name'] == term
        assert [{'count': 1, 'entity': 'company'}] == response.data['aggregations']

    @pytest.mark.parametrize(
        'field,value,term,match',
        (
            ('trading_address_postcode', 'SW1A 1AA', 'SW1A 1AA', True),
            ('trading_address_postcode', 'SW1A 1AA', 'SW1A 1AB', False),
            ('registered_address_postcode', 'SW1A 1AA', 'SW1A 1AA', True),
            ('registered_address_postcode', 'SW1A 1AA', 'SW1A 1AB', False),
        )
    )
    def test_search_in_field(self, setup_es, field, value, term, match):
        """Tests basic aggregate companies query."""
        CompanyFactory()
        CompanyFactory(**{field: value})
        setup_es.indices.refresh()

        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': term,
            'entity': 'company'
        })

        assert response.status_code == status.HTTP_200_OK
        if match:
            assert response.data['count'] == 1
            assert response.data['results'][0][field] == value
        else:
            assert response.data['count'] == 0

    def test_no_results(self, setup_data):
        """Tests case where there should be no results."""
        term = 'there-should-be-no-match'

        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {
            'term': term,
            'entity': 'company'
        })

        assert response.data['count'] == 0

    def test_companies_no_term(self, setup_data):
        """Tests case where there is not term provided."""
        url = reverse('api-v3:search:basic')
        response = self.api_client.get(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSearchExport(APITestMixin):
    """Tests search export views."""

    @staticmethod
    def _get_random_constant_id(constant):
        """Gets random constant id."""
        return random.choice(list(constant)).value.id

    @staticmethod
    def _get_random_list_of_constant_ids(constant, max=10):
        """Gets list of random constant ids."""
        return {TestSearchExport._get_random_constant_id(constant) for _ in range(max)}

    def _create_company(self, name_prefix, archived=False):
        country = TestSearchExport._get_random_constant_id(constants.Country)
        ch = CompaniesHouseCompanyFactory()
        name = f"{name_prefix} {factory.Faker('word').generate({})}"
        data = {
            'account_manager': AdviserFactory(),
            'alias': factory.Faker('text'),
            'archived': archived,
            'business_type_id':
                TestSearchExport._get_random_constant_id(BusinessTypeConstant),
            'classification_id': random_obj_for_model(CompanyClassification).pk,
            'company_number': ch.company_number,
            'created_on': factory.Faker('date_object'),
            'description': factory.Faker('text'),
            'employee_range_id':
                TestSearchExport._get_random_constant_id(constants.EmployeeRange),
            'headquarter_type_id':
                TestSearchExport._get_random_constant_id(constants.HeadquarterType),
            'modified_on': factory.Faker('date_object'),
            'name': name,
            'one_list_account_owner': AdviserFactory(),
            'registered_address_1': factory.Faker('street_name'),
            'registered_address_country_id': country,
            'registered_address_county': factory.Faker('name'),
            'registered_address_postcode': factory.Faker('postcode'),
            'registered_address_town': factory.Faker('city'),
            'sector_id': TestSearchExport._get_random_constant_id(constants.Sector),
            'trading_address_1': factory.Faker('street_name'),
            'trading_address_country_id':
                TestSearchExport._get_random_constant_id(constants.Country),
            'trading_address_county': factory.Faker('name'),
            'trading_address_postcode': factory.Faker('postcode'),
            'trading_address_town': factory.Faker('city'),
            'turnover_range_id':
                TestSearchExport._get_random_constant_id(constants.TurnoverRange),
            'website': factory.Faker('url'),
        }
        if country == constants.Country.united_kingdom.value.id:
            data['uk_region_id'] = TestSearchExport._get_random_constant_id(constants.UKRegion)
        if archived:
            data.update({
                'archived_by': AdviserFactory(),
                'archived_on': factory.Faker('date_object'),
                'archived_reason': factory.Faker('text'),
            })

        company = CompanyFactory(
            **data
        )
        company.contacts.set(
            ContactFactory.create_batch(2)
        )
        company.export_to_countries.set(
            TestSearchExport._get_random_list_of_constant_ids(constants.Country)
        )
        company.future_interest_countries.set(
            TestSearchExport._get_random_list_of_constant_ids(constants.Country)
        )
        company.save()
        return company
