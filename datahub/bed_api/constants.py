from collections import namedtuple
from enum import Enum

QueryConstant = namedtuple('QueryConstant', ('sql', 'arg'))


class ContactQuery(Enum):
    """Contact Salesforce Queries"""

    get_by_id = QueryConstant(
        'SELECT Id FROM Contact WHERE Id = {id}',
        'id',
    )
    get_email_by_id = QueryConstant(
        'SELECT Id, Email FROM Contact WHERE Id = {id}',
        'id',
    )
    get_notes_by_id = QueryConstant(
        'SELECT Id, Notes__c FROM Contact WHERE Id = {id}',
        'id',
    )


class AccountQuery(Enum):
    """Account Salesforce Queries"""

    get_by_id = QueryConstant(
        'SELECT Id FROM Account WHERE Id = {id}',
        'id',
    )
    get_name_by_id = QueryConstant('SELECT Id, Name FROM Account WHERE Id = {id}', 'id')


class Salutation(str, Enum):
    """Salutations from BED"""

    mr = 'Mr.'
    mrs = 'Mrs.'
    miss = 'Miss'
    ms = 'Ms.'
    dr = 'Dr.'
    prof = 'Prof.'
    right_honourable = 'Rt Hon.'
    sir = 'Sir'
    lord = 'Lord'
    dame = 'Dame'


class ContactType(str, Enum):
    """Contact Types from BED"""

    hmg_contact = 'HMG Contact'
    external = 'External Attendees'


class JobType(str, Enum):
    """Job Types from BED"""

    ceo = 'CEO'
    chairperson = 'Chairperson'
    communications = 'Communications'
    consultant = 'Consultant'
    corporate_social_responsibility = 'Corporate Social Responsibility'
    director = 'Director'
    education = 'Education'
    engineering = 'Engineering'
    executive = 'Executive'
    finance = 'Finance'
    financial_director = 'Financial Director'
    founder = 'Founder'
    head_of_public_affairs = 'Head of Public Affairs'
    health_professional = 'Health Professional'
    hr = 'HR'
    legal = 'Legal'
    manager = 'Manager'
    operations = 'Operations'
    other = 'Other'
    owner = 'Owner'
    policy = 'Policy'
    president = 'President'
    public_affairs = 'Public Affairs'


class BusinessArea(str, Enum):
    """Business Area Types from BED"""

    advanced_manufacturing = 'Advanced Manufacturing'
    professional = 'Professional & Business Services'
    civil_society = 'Civil Society'
    consumer_and_retail = 'Consumer & Retail'
    creative_industries = 'Creative Industries'
    defense = 'Defence'
    education_and_research = 'Education & Research'
    energy = 'Energy'
    environmental_services = 'Environmental Services'
    financial_services = 'Financial Services'
    food_and_agriculture = 'Food & Agriculture'


class HighLevelSector(str, Enum):
    """High Level Sector Types from BED"""

    advanced_manufacturing = 'Advanced Manufacturing'
    civil_society = 'Civil Society'
    consumer_and_retail = 'Consumer & Retail'
    creative_industries = 'Creative Industries'
    defense = 'Defence'
    education_and_research = 'Education & Research'
    energy = 'Energy'
    environmental_services = 'Environmental Services'
    financial_services = 'Financial Services'
    food_and_agriculture = 'Food & Agriculture'


class LowLevelSector(str, Enum):
    """Low Level Sector Types from BED"""

    consumers = 'Consumers'
    retail = 'Retail'
    digital = 'Digital'
    digital_infrastructure = 'Digital Infrastructure'
    real_estate = 'Real Estate'
    telecoms = 'Telecoms'
