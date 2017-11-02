from datahub.investment import models
from datahub.metadata.fixtures import Fixture
from datahub.metadata.registry import registry


class InvestmentFixtures(Fixture):
    """Metadata fixtures (for the loadmetadata command)."""

    files = [
        'fixtures/investor_types.yaml',
        'fixtures/involvements.yaml',
        'fixtures/specific_programmes.yaml',
    ]


registry.register(
    metadata_id='investment-specific-programme',
    model=models.SpecificProgramme,
)

registry.register(
    metadata_id='investment-investor-type',
    model=models.InvestorType,
)

registry.register(
    metadata_id='investment-involvement',
    model=models.Involvement,
)
