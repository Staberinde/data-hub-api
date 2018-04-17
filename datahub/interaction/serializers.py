from operator import not_

from django.utils.translation import ugettext_lazy
from rest_framework import serializers

from datahub.company.models import Company, Contact
from datahub.company.serializers import NestedAdviserField
from datahub.core.serializers import NestedRelatedField
from datahub.core.validate_utils import is_blank, is_not_blank
from datahub.core.validators import (
    AnyIsNotBlankRule, EqualsRule, InRule, OperatorRule, RulesBasedValidator, ValidationRule
)
from datahub.event.models import Event
from datahub.investment.models import InvestmentProject
from datahub.metadata.models import Service, Team
from .models import (CommunicationChannel, Interaction, PolicyArea, PolicyIssueType,
                     ServiceDeliveryStatus)
from .permissions import HasAssociatedInvestmentProjectValidator


class InteractionSerializer(serializers.ModelSerializer):
    """V3 interaction serialiser."""

    default_error_messages = {
        'missing_entity': ugettext_lazy(
            'A company or investment_project must be provided.'
        ),
        'invalid_for_non_service_delivery': ugettext_lazy(
            'This field is only valid for service deliveries.'
        ),
        'invalid_for_service_delivery': ugettext_lazy(
            'This field is not valid for service deliveries.'
        ),
        'invalid_for_non_interaction': ugettext_lazy(
            'This field is only valid for interactions.'
        ),
        'invalid_for_non_event': ugettext_lazy(
            'This field is only valid for event service deliveries.'
        ),
        'invalid_for_non_policy_feedback': ugettext_lazy(
            'This field is only valid for policy feedback.'
        ),
    }

    company = NestedRelatedField(Company, required=False, allow_null=True)
    contact = NestedRelatedField(Contact)
    dit_adviser = NestedAdviserField()
    created_by = NestedAdviserField(read_only=True)
    dit_team = NestedRelatedField(Team)
    communication_channel = NestedRelatedField(
        CommunicationChannel, required=False, allow_null=True
    )
    is_event = serializers.NullBooleanField(required=False)
    event = NestedRelatedField(Event, required=False, allow_null=True)
    investment_project = NestedRelatedField(
        InvestmentProject, required=False, allow_null=True, extra_fields=('name', 'project_code')
    )
    modified_by = NestedAdviserField(read_only=True)
    service = NestedRelatedField(Service)
    service_delivery_status = NestedRelatedField(
        ServiceDeliveryStatus, required=False, allow_null=True
    )
    policy_area = NestedRelatedField(
        PolicyArea, required=False, allow_null=True
    )
    policy_issue_type = NestedRelatedField(
        PolicyIssueType, required=False, allow_null=True
    )

    def validate(self, data):
        """
        Removes the semi-virtual field is_event from the data.

        This is removed because the value is not stored; it is instead inferred from contents
        of the the event field during serialisation.
        """
        if 'is_event' in data:
            del data['is_event']
        return data

    class Meta:
        model = Interaction
        extra_kwargs = {
            # Date is a datetime in the model, but only the date component is used
            # (at present). Setting the formats as below effectively makes the field
            # behave like a date field without changing the schema and breaking the
            # v1 API.
            'date': {'format': '%Y-%m-%d', 'input_formats': ['%Y-%m-%d']},
            'grant_amount_offered': {'min_value': 0},
            'net_company_receipt': {'min_value': 0},
        }
        fields = (
            'id',
            'company',
            'contact',
            'created_on',
            'created_by',
            'event',
            'is_event',
            'kind',
            'modified_by',
            'modified_on',
            'date',
            'dit_adviser',
            'dit_team',
            'communication_channel',
            'grant_amount_offered',
            'investment_project',
            'net_company_receipt',
            'service',
            'service_delivery_status',
            'subject',
            'notes',
            'archived_documents_url_path',
            'policy_area',
            'policy_issue_type',
        )
        read_only_fields = (
            'archived_documents_url_path',
        )
        validators = [
            HasAssociatedInvestmentProjectValidator(),
            RulesBasedValidator(
                ValidationRule(
                    'required',
                    OperatorRule('communication_channel', bool),
                    when=InRule('kind', [
                        Interaction.KINDS.interaction,
                        Interaction.KINDS.policy_feedback
                    ]),
                ),
                ValidationRule(
                    'required',
                    OperatorRule('company', bool),
                    when=InRule('kind', [
                        Interaction.KINDS.service_delivery,
                        Interaction.KINDS.policy_feedback
                    ]),
                ),
                ValidationRule(
                    'invalid_for_non_interaction',
                    OperatorRule('investment_project', not_),
                    when=InRule('kind', [
                        Interaction.KINDS.service_delivery,
                        Interaction.KINDS.policy_feedback
                    ]),
                ),
                ValidationRule(
                    'missing_entity',
                    AnyIsNotBlankRule('company', 'investment_project'),
                    when=EqualsRule('kind', Interaction.KINDS.interaction),
                ),
                ValidationRule(
                    'invalid_for_service_delivery',
                    OperatorRule('communication_channel', not_),
                    when=EqualsRule('kind', Interaction.KINDS.service_delivery),
                ),
                ValidationRule(
                    'invalid_for_non_service_delivery',
                    OperatorRule('is_event', is_blank),
                    OperatorRule('event', is_blank),
                    OperatorRule('service_delivery_status', is_blank),
                    OperatorRule('grant_amount_offered', is_blank),
                    OperatorRule('net_company_receipt', is_blank),
                    when=InRule('kind', [
                        Interaction.KINDS.interaction,
                        Interaction.KINDS.policy_feedback
                    ]),
                ),
                ValidationRule(
                    'invalid_for_non_policy_feedback',
                    OperatorRule('policy_area', is_blank),
                    OperatorRule('policy_issue_type', is_blank),
                    when=InRule('kind', [
                        Interaction.KINDS.interaction,
                        Interaction.KINDS.service_delivery,
                    ])
                ),
                ValidationRule(
                    'required',
                    OperatorRule('is_event', is_not_blank),
                    when=EqualsRule('kind', Interaction.KINDS.service_delivery),
                ),
                ValidationRule(
                    'required',
                    OperatorRule('policy_area', is_not_blank),
                    OperatorRule('policy_issue_type', is_not_blank),
                    when=EqualsRule('kind', Interaction.KINDS.policy_feedback),
                ),
                ValidationRule(
                    'required',
                    OperatorRule('event', bool),
                    when=OperatorRule('is_event', bool),
                ),
                ValidationRule(
                    'invalid_for_non_event',
                    OperatorRule('event', not_),
                    when=OperatorRule('is_event', not_),
                ),
            ),
        ]
