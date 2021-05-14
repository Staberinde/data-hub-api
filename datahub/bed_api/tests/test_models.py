from freezegun import freeze_time

from datahub.bed_api.constants import Salutation
from datahub.bed_api.models import EditContact


class TestEditContactShould:
    """
    Contact expectations
    """

    def test_contact_name_outputs_full_name(self):
        """
        Should format contact name accordingly
        """
        contact = EditContact(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@email.com',
        )
        contact.Salutation = Salutation.mrs
        contact.MiddleName = 'Middle'
        contact.Suffix = 'Teacher'

        assert contact.name == 'Mrs. Jane Middle Doe Teacher'

    def test_contact_name_outputs_partial_full_name(self):
        """
        Should format contact name accordingly
        """
        contact = EditContact(
            first_name=None,
            last_name='Doe',
            email='jane.doe@email.com',
        )
        contact.Salutation = Salutation.mr

        assert contact.name == 'Mr. Doe'

    @freeze_time('2020-01-01-12:00:00')
    def test_contact_outputs_value_only_generated_dictionary(self):
        """
        Should output contact as dictionary without name, calculated fields
        and empty values
        """
        expected = {
            'Email': 'john.doe@email.com',
            'FirstName': 'John',
            'Id': 'Test_Identity',
            'LastName': 'Doe',
            'Salutation': 'Mr.',
        }

        contact = EditContact(
            first_name='John',
            last_name='Doe',
            email='john.doe@email.com',
        )
        contact.Salutation = Salutation.mr
        contact.Id = 'Test_Identity'
        assert contact.as_values_only_dict() == expected
