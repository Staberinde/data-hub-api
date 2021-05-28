from unittest import mock

from datahub.bed_api.entities import EventAttendee
from datahub.bed_api.repositories import EventAttendeeRepository
from datahub.bed_api.tests.test_utils import (
    create_fail_query_response,
    create_success_query_response,
)


class TestEventAttendeeRepositoryShould:
    """Unit tests for EventAttendeeRepository"""

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_add_calls_salesforce_event_attendee_add_with_valid_args(
        self,
        mock_salesforce,
        generate_event_attendee: EventAttendee,
    ):
        """
        Test add calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        :param generate_event_attendee: Generated event atttendee data
        """
        repository = EventAttendeeRepository(mock_salesforce)

        repository.add(generate_event_attendee.as_values_only_dict())

        assert mock_salesforce.Event_Attendee__c.create.called
        assert mock_salesforce.Event_Attendee__c.create.call_args == mock.call(
            generate_event_attendee.as_values_only_dict(),
        )

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_delete_calls_salesforce_event_attendee_delete_with_valid_args(
        self,
        mock_salesforce,
    ):
        """
        Test delete calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'

        repository.delete(expected_record_id)

        assert mock_salesforce.Event_Attendee__c.delete.called
        assert mock_salesforce.Event_Attendee__c.delete.call_args == mock.call(
            expected_record_id,
        )

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_exists_return_true_when_query_response_succeeds(
        self,
        mock_salesforce,
    ):
        """
        Test exists calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'
        success_query_response = create_success_query_response(
            'Event_Attendee__c',
            expected_record_id,
        )

        with mock.patch(
            'datahub.bed_api.repositories.EventAttendeeRepository.query',
            return_value=success_query_response,
        ):
            exists_response = repository.exists(expected_record_id)

            assert exists_response is True

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_exists_return_false_when_query_response_fails(
        self,
        mock_salesforce,
    ):
        """
        Test exists calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'
        failed_query_response = create_fail_query_response()

        with mock.patch(
            'datahub.bed_api.repositories.EventAttendeeRepository.query',
            return_value=failed_query_response,
        ):
            exists_response = repository.exists(expected_record_id)

            assert exists_response is False

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_get_calls_salesforce_event_attendee_get_with_valid_args(
        self,
        mock_salesforce,
    ):
        """
        Test get calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'

        repository.get(expected_record_id)

        assert mock_salesforce.Event_Attendee__c.get.called
        assert mock_salesforce.Event_Attendee__c.get.call_args == mock.call(
            expected_record_id,
        )

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_get_by_datahub_id_calls_salesforce_contact_get_with_valid_args(
            self,
            mock_salesforce,
    ):
        """
        Test get_by calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'

        repository.get_by_datahub_id(expected_record_id)

        assert mock_salesforce.Event_Attendee__c.get_by_custom_id.called
        assert mock_salesforce.Event_Attendee__c.get_by_custom_id.call_args == mock.call(
            'Datahub_ID__c',
            expected_record_id,
        )

    @mock.patch('datahub.bed_api.factories.Salesforce')
    def test_update_calls_salesforce_event_attendee_update_with_valid_args(
        self,
        mock_salesforce,
        generate_event_attendee: EventAttendee,
    ):
        """
        Test update calls Salesforce with the correct Arguments
        :param mock_salesforce: Monkeypatch for Salesforce
        :param generate_event_attendee: Generated event attendee data
        """
        repository = EventAttendeeRepository(mock_salesforce)
        expected_record_id = 'test_record_id'
        generate_event_attendee.id = expected_record_id

        repository.update(expected_record_id, generate_event_attendee.as_values_only_dict())

        assert mock_salesforce.Event_Attendee__c.update.called
        assert mock_salesforce.Event_Attendee__c.update.call_args == mock.call(
            'test_record_id',
            generate_event_attendee.as_values_only_dict(),
        )
