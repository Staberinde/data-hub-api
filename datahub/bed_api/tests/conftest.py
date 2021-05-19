import datetime
import uuid

import pytest

from datahub.bed_api.constants import (
    BusinessArea,
    Classification,
    ContactType,
    DepartmentEyes,
    HighLevelSector,
    InteractionType,
    IssueType,
    JobType,
    LowLevelSector,
    PolicyArea,
    Salutation,
    SectorsAffected,
    Sentiment,
    TopIssuesByRank,
    TransparencyStatus,
)
from datahub.bed_api.factories import BedFactory
from datahub.bed_api.models import (
    EditAccount,
    EditContact,
    EditEvent,
    EditEventAttendee, EditPolicyIssues,
)
from datahub.bed_api.repositories import (
    AccountRepository,
    ContactRepository,
    EventAttendeeRepository,
    EventRepository,
    PolicyIssuesRepository,
)
from datahub.bed_api.tests.test_utils import remove_newline
from datahub.core.constants import Country, UKRegion


@pytest.fixture
def salesforce():
    """Create salesforce instance using the BedFactory"""
    bed_factory = BedFactory()
    salesforce = bed_factory.create()
    return salesforce


@pytest.fixture
def contact_repository(salesforce):
    """
    Creates instance of contact repository
    :param salesforce: BedFactory creating an instance of salesforce
    :return: Instance of ContactRepository
    """
    repository = ContactRepository(salesforce)
    return repository


@pytest.fixture
def account_repository(salesforce):
    """
    Creates instance of account repository
    :param salesforce: BedFactory creating an instance of salesforce
    :return: Instance of AccountRepository
    """
    repository = AccountRepository(salesforce)
    return repository


@pytest.fixture
def event_repository(salesforce):
    """
    Creates instance of event repository
    :param salesforce: BedFactory creating an instance of salesforce
    :return: Instance of EventRepository
    """
    repository = EventRepository(salesforce)
    return repository


@pytest.fixture
def event_attendee_repository(salesforce):
    """
    Creates instance of event repository
    :param salesforce: BedFactory creating an instance of salesforce
    :return: Instance of EventRepository
    """
    repository = EventAttendeeRepository(salesforce)
    return repository


@pytest.fixture
def policy_issues_repository(salesforce):
    """
    Creates instance of policy issues repository
    :param salesforce: BedFactory creating an instance of salesforce
    :return: Instance of EventRepository
    """
    repository = PolicyIssuesRepository(salesforce)
    return repository


@pytest.fixture
def generate_high_level_sector(faker):
    """
    Generate random high level sector
    :param faker: Faker Library
    :return: Random high level sector value
    """
    high_level_sector = faker.random_element(
        elements=(
            HighLevelSector.defense,
            HighLevelSector.food_and_agriculture,
            HighLevelSector.energy,
            HighLevelSector.financial_services,
            HighLevelSector.environmental_services,
            HighLevelSector.education_and_research,
            HighLevelSector.creative_industries,
            HighLevelSector.advanced_manufacturing,
        ),
    )
    return high_level_sector


@pytest.fixture
def generate_low_level_sector(faker):
    """
    Generate random low level sector
    :param faker: Faker Library
    :return: Random low level sector value
    """
    low_level_sector = faker.random_element(
        elements=(
            LowLevelSector.consumers,
            LowLevelSector.digital,
            LowLevelSector.digital_infrastructure,
            LowLevelSector.retail,
            LowLevelSector.real_estate,
            LowLevelSector.telecoms,
        ),
    )
    return low_level_sector


@pytest.fixture
def generate_uk_region_name(faker):
    """
    Generate random UK Region name
    :param faker: Faker Library
    :return: Random UK region name value
    """
    uk_region = faker.random_element(
        elements=(
            UKRegion.all.value.name,
            UKRegion.channel_islands.value.name,
            UKRegion.alderney.value.name,
            UKRegion.england.value.name,
            UKRegion.east_midlands.value.name,
            UKRegion.east_of_england.value.name,
            UKRegion.fdi_hub.value.name,
            UKRegion.guernsey.value.name,
            UKRegion.isle_of_man.value.name,
            UKRegion.jersey.value.name,
            UKRegion.london.value.name,
            UKRegion.north_east.value.name,
            UKRegion.north_west.value.name,
            UKRegion.northern_ireland.value.name,
            UKRegion.sark.value.name,
            UKRegion.scotland.value.name,
            UKRegion.south_west.value.name,
            UKRegion.south_east.value.name,
            UKRegion.ukti_dubai_hub.value.name,
            UKRegion.wales.value.name,
            UKRegion.yorkshire_and_the_humber.value.name,
            UKRegion.west_midlands.value.name,
        ),
    )
    return uk_region


@pytest.fixture
def generate_salutation(faker):
    """
    Generate random salutation
    :param faker: Faker Library
    :return: Random salutation value
    """
    salutation = faker.random_element(
        elements=(
            Salutation.mrs,
            Salutation.mr,
            Salutation.prof,
            Salutation.dame,
            Salutation.dr,
            Salutation.lord,
            Salutation.miss,
            Salutation.ms,
            Salutation.sir,
            Salutation.right_honourable,
        ),
    )
    return salutation


@pytest.fixture
def generate_country_names(faker):
    """
    Generate random country names array
    :param faker: Faker Library
    :return: Random country names value
    """
    countries = faker.random_elements(
        elements=(
            Country.argentina.value.name,
            Country.azerbaijan.value.name,
            Country.cayman_islands.value.name,
            Country.japan.value.name,
            Country.canada.value.name,
            Country.france.value.name,
            Country.greece.value.name,
            Country.ireland.value.name,
            Country.italy.value.name,
            Country.united_states.value.name,
            Country.united_kingdom.value.name,
        ),
        unique=True,
    )
    return sorted(countries)


@pytest.fixture
def generate_issue_types(faker):
    """
    Generate random issue types array
    :param faker: Faker Library
    :return: Random issue topics value
    """
    issue_types = faker.random_elements(
        elements=(
            IssueType.covid_19,
            IssueType.economic_risk,
            IssueType.domestic_policy,
            IssueType.economic_opportunity,
            IssueType.international_climate,
            IssueType.uk_transition_policy,
        ),
        unique=True,
    )
    return sorted(issue_types)


@pytest.fixture
def generate_job_type(faker):
    """
    Generate random job type
    :param faker: Faker Library
    :return: Random JobType value
    """
    job_type = faker.random_element(
        elements=(
            JobType.consultant,
            JobType.hr,
            JobType.ceo,
            JobType.chairperson,
            JobType.communications,
            JobType.corporate_social_responsibility,
            JobType.director,
            JobType.education,
            JobType.engineering,
            JobType.executive,
            JobType.finance,
            JobType.financial_director,
            JobType.founder,
            JobType.head_of_public_affairs,
            JobType.health_professional,
            JobType.head_of_public_affairs,
            JobType.hr,
            JobType.legal,
            JobType.manager,
            JobType.operations,
            JobType.other,
            JobType.owner,
            JobType.policy,
            JobType.president,
            JobType.public_affairs,
        ),
    )
    return job_type


@pytest.fixture
def generate_business_area(faker):
    """
    Generate random business area
    :param faker: Faker Library
    :return: Random BusinessArea value
    """
    business_area = faker.random_element(
        elements=(
            BusinessArea.advanced_manufacturing,
            BusinessArea.civil_society,
            BusinessArea.consumer_and_retail,
            BusinessArea.creative_industries,
            BusinessArea.defense,
            BusinessArea.education_and_research,
            BusinessArea.energy,
            BusinessArea.environmental_services,
            BusinessArea.financial_services,
            BusinessArea.food_and_agriculture,
            BusinessArea.professional,
        ),
    )
    return business_area


@pytest.fixture
def generate_interaction_type(faker):
    """
    Generate random interaction type
    :param faker: Faker Library
    :return: Random interaction type
    """
    company_number = faker.random_element(
        elements=(
            InteractionType.forum,
            InteractionType.letter,
            InteractionType.email,
            InteractionType.bilateral_meeting,
            InteractionType.brush_by,
            InteractionType.conference,
            InteractionType.multilateral_meeting,
            InteractionType.phone_call,
            InteractionType.reception,
            InteractionType.roadshow,
        ),
    )
    return company_number


@pytest.fixture
def generate_company_number(faker):
    """
    Generate random company number
    :param faker: Faker Library
    :return: Random company value
    """
    company_number = faker.random_element(
        elements=(
            '06591591',
            '6431544',
            '31079',
            '39740',
            '6935579',
            '10002309',
            '11163479',
        ),
    )
    return company_number


@pytest.fixture
def generate_transparency_status(faker):
    """
    Generate random transparency status
    :param faker: Faker Library
    :return: Random transparency status
    """
    transparency_status = faker.random_element(
        elements=(
            TransparencyStatus.delete,
            TransparencyStatus.draft,
            TransparencyStatus.confirm,
        ),
    )
    return transparency_status


@pytest.fixture
def generate_sentiment(faker):
    """
    Generate sentiment
    :param faker: Faker Library
    :return: Random sentiment
    """
    sentiment = faker.random_element(
        elements=(
            Sentiment.negative,
            Sentiment.neutral,
            Sentiment.positive,
        ),
    )
    return sentiment


@pytest.fixture
def generate_department_eyes(faker):
    """
    Generate random department eyes
    :param faker: Faker Library
    :return: Random transparency status
    """
    department_eyes_only = faker.random_element(
        elements=(
            DepartmentEyes.advanced_manufacturing,
            DepartmentEyes.creative_industries,
            DepartmentEyes.energy,
            DepartmentEyes.environmental_services,
            DepartmentEyes.financial_services,
            DepartmentEyes.food_and_agriculture,
            DepartmentEyes.consumer_and_retail,
            DepartmentEyes.civil_society,
            DepartmentEyes.aviation,
            DepartmentEyes.defence,
        ),
    )
    return department_eyes_only


@pytest.fixture
def generate_policy_area(faker):
    """
    Generate random policy_area
    :param faker: Faker Library
    :return: Random policy area
    """
    policy_area = faker.random_element(
        elements=(
            PolicyArea.access_to_finance,
            PolicyArea.access_to_public_funding,
            PolicyArea.agriculture,
            PolicyArea.announcement_feedback,
            PolicyArea.art_culture_sport_and_leisure,
            PolicyArea.business_regulation,
            PolicyArea.company_law_and_company_reporting,
            PolicyArea.cybersecurity,
            PolicyArea.competition_law_and_policy,
            PolicyArea.customs_union,
            PolicyArea.consumer_rights,
            PolicyArea.cop26_adaptation_and_resilience,
            PolicyArea.cop26_clean_transport,
            PolicyArea.cop26_energy_transitions,
            PolicyArea.cop26_finance,
            PolicyArea.energy,
            PolicyArea.other,
        ),
    )
    return policy_area


@pytest.fixture
def generate_classification(faker):
    """
    Generate random Classification
    :param faker: Faker Library
    :return: Random Classification
    """
    classification = faker.random_element(
        elements=(
            Classification.official,
            Classification.official_sensitive,
            Classification.unclassified,
        ),
    )
    return classification


@pytest.fixture
def generate_sectors_affected(faker):
    """
    Generate random SectorsAffected
    :param faker: Faker Library
    :return: Random SectorsAffected
    """
    sectors_affected = faker.random_element(
        elements=(
            SectorsAffected.advanced_manufacturing,
            SectorsAffected.consumer_and_retail,
            SectorsAffected.creative_industries,
            SectorsAffected.civil_society,
            SectorsAffected.defense,
            SectorsAffected.education_and_research,
            SectorsAffected.energy,
            SectorsAffected.environmental_services,
            SectorsAffected.financial_services,
            SectorsAffected.food_and_agriculture,
            SectorsAffected.health_and_social_care,
            SectorsAffected.infrastructure_construction_and_housing,
            SectorsAffected.justice_rights_and_equality,
            SectorsAffected.life_sciences,
            SectorsAffected.materials,
            SectorsAffected.media_and_broadcasting,
            SectorsAffected.pan_economy_trade_body,
            SectorsAffected.professional_and_business_services,
            SectorsAffected.tech_and_telecoms,
            SectorsAffected.tourism,
            SectorsAffected.transport,
        ),
    )
    return sectors_affected


@pytest.fixture
def generate_account(
    faker,
    generate_high_level_sector,
    generate_low_level_sector,
    generate_uk_region_name,
    generate_country_names,
    generate_company_number,
):
    """
    Generate account with random data
    :param faker: Faker Library
    :param generate_high_level_sector: sector mapping
    :param generate_low_level_sector: sector mapping
    :param generate_uk_region_name: uk regions
    :param generate_country_names: country names
    :param generate_company_number: company numbers
    :return: New EditAccount with random values
    """
    new_account = EditAccount(
        name=faker.company(),
        high_level_sector=generate_high_level_sector,
        low_level_sector=generate_low_level_sector,
    )
    new_account.BillingStreet = faker.street_address()
    new_account.BillingCity = faker.city()
    new_account.BillingState = faker.street_name()
    new_account.BillingPostalCode = faker.postcode()
    new_account.BillingCountry = faker.country()
    new_account.ShippingStreet = faker.street_name()
    new_account.ShippingCity = faker.city()
    new_account.ShippingState = faker.street_name()
    new_account.ShippingPostalCode = faker.postcode()
    new_account.ShippingCountry = faker.country()
    new_account.UK_Region__c = generate_uk_region_name
    new_account.Country_HQ__c = faker.random_element(elements=generate_country_names)
    # check: # Unable to create/update fields: Company_size__c.
    #          Please check the security settings of this field and verify that it is read/write
    # new_account.Company_size__c = faker.random_int()
    # Removed as this gets duplicate errors when the same values are recycled
    # new_account.Company_Number__c = generate_company_number
    # new_account.Companies_House_ID__c = generate_company_number
    new_account.Location__c = faker.country()
    new_account.Company_Website__c = faker.url()

    return new_account


@pytest.fixture
def generate_contact(
    faker,
    generate_salutation,
    generate_job_type,
    generate_business_area,
):
    """
    Generate new EditContact with random values
    :param faker: Faker Library
    :param generate_salutation:
    :param generate_job_type:
    :param generate_business_area:
    :return: New EditContact with random fake data
    """
    firstname = faker.first_name()
    lastname = faker.last_name()
    email = f'{firstname.lower()}.{lastname.lower()}@digital.trade.gov.uk'
    contact = EditContact(
        datahub_id=str(uuid.uuid4()),
        first_name=firstname,
        last_name=lastname,
        email=email,
        account_id=str(uuid.uuid4()),
    )
    contact.Salutation = generate_salutation
    contact.Suffix = faker.suffix()
    contact.MiddleName = faker.first_name()
    contact.Phone = faker.phone_number()
    contact.MobilePhone = faker.phone_number()
    contact.Notes__c = faker.text(max_nb_chars=100)
    contact.Contact_Type__c = ContactType.external
    contact.Job_Title__c = faker.job()
    contact.Job_Type__c = generate_job_type
    contact.Business_Area__c = generate_business_area
    contact.AssistantName = faker.name()
    contact.Assistant_Email__c = faker.company_email()
    contact.Assistant_Phone__c = faker.phone_number()
    return contact


@pytest.fixture
def generate_event(
    faker,
    generate_interaction_type,
    generate_uk_region_name,
    generate_transparency_status,
    generate_issue_types,
    generate_department_eyes,
):
    """
    Generate new EditEvent with random values
    :param faker: Faker Library
    :param generate_interaction_type: Random generate InteractionType
    :param generate_uk_region_name: Random uk region
    :param generate_transparency_status: Random transparency status
    :param generate_issue_types: Random issue topics array
    :param generate_department_eyes: Random department eyes only value
    :return: New EditEvent with random fake data
    """
    event = EditEvent(
        name=f'Event Integration Test {datetime.datetime.today()}',
        datahub_id=str(uuid.uuid4()),
        title=remove_newline(faker.text()),
    )
    event.Date__c = faker.date()
    event.Description__c = faker.text()
    event.Interaction_Type__c = generate_interaction_type
    event.Webinar_Information__c = faker.text()
    event.Address__c = faker.address()
    event.Location__c = faker.street_address()
    event.City_Town__c = faker.city()
    event.Region__c = generate_uk_region_name
    event.Country__c = faker.country()
    event.Attendees__c = faker.text()
    event.Contacts_to_share__c = faker.text()
    event.iCal_UID__c = str(uuid.uuid4())
    event.Transparency_Reason_for_meeting__c = faker.text()
    event.Transparency_Status__c = generate_transparency_status
    event.Issue_Topics__c = ';'.join(generate_issue_types)
    event.HMG_Lead__c = faker.company_email()
    event.Department_Eyes_Only__c = generate_department_eyes
    return event


@pytest.fixture
def generate_event_attendee(
    faker,
):
    """
    Generate new Event Attendee test data
    :param faker: Faker data generator
    """
    event_attendee = EditEventAttendee(
        datahub_id=str(uuid.uuid4()),
        event_id=str(uuid.uuid4()),
        contact_id=str(uuid.uuid4()),
    )
    event_attendee.Name_stub__c = f'Event Attendee Integration Test {datetime.datetime.today()}'
    event_attendee.Email__c = faker.company_email()
    return event_attendee


@pytest.fixture
def generate_policy_issues(
    faker,
    generate_issue_types,
    generate_uk_region_name,
    generate_policy_area,
    generate_sentiment,
    generate_classification,
    generate_sectors_affected,
):
    """
    Generate new Event Attendee test data
    :param faker: Faker data generator
    :param generate_issue_types: Data generated for issue types
    :param generate_uk_region_name: Data generated for uk regions
    :param generate_policy_area: Data generated for policy area
    :param generate_sentiment: Data generated for sentiment
    :param generate_classification: Data generated for classification
    :param generate_sectors_affected: Data generated for sectors effected
    """
    policy_issues = EditPolicyIssues(
        name=f'Policy Issues Integration Test {datetime.datetime.today()}',
        datahub_id=str(uuid.uuid4()),
        issue_type=';'.join(generate_issue_types),
        account_id=str(uuid.uuid4()),
        policy_area=generate_policy_area,
        sentiment=generate_sentiment,
        classification=generate_classification,
        sectors_affected=generate_sectors_affected,
        uk_region_affected=generate_uk_region_name,
    )
    policy_issues.Add_Interactions__c = str(uuid.uuid4())  # Interaction id
    policy_issues.Description_of_Issue__c = faker.text()
    policy_issues.Top_3_Issue__c = TopIssuesByRank.eight
    policy_issues.Location_s_Affected__c = generate_uk_region_name
    policy_issues.UK_Affected__c = generate_uk_region_name
    # TODO: Non mandatory fields
    return policy_issues
