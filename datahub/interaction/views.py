from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import IsAuthenticatedOrTokenHasScope
from rest_framework.filters import OrderingFilter

from datahub.core.viewsets import CoreViewSet
from datahub.interaction.permissions import (
    InteractionModelPermissions,
    IsAssociatedToInvestmentProjectInteractionFilter,
    IsAssociatedToInvestmentProjectInteractionPermission,
    PolicyFeedbackObjectPermission,
    PolicyFeedbackPermissionFilter,
)
from datahub.interaction.queryset import get_interaction_queryset
from datahub.interaction.serializers import InteractionSerializer
from datahub.oauth.scopes import Scope


class InteractionViewSet(CoreViewSet):
    """Interaction ViewSet v3."""

    required_scopes = (Scope.internal_front_end,)
    permission_classes = (
        IsAuthenticatedOrTokenHasScope,
        InteractionModelPermissions,
        IsAssociatedToInvestmentProjectInteractionPermission,
        PolicyFeedbackObjectPermission,
    )
    serializer_class = InteractionSerializer
    queryset = get_interaction_queryset()
    filter_backends = (
        DjangoFilterBackend,
        IsAssociatedToInvestmentProjectInteractionFilter,
        OrderingFilter,
        PolicyFeedbackPermissionFilter,
    )
    filterset_fields = ['company_id', 'contact_id', 'event_id', 'investment_project_id']
    ordering_fields = (
        'company__name',
        'contact__first_name',
        'contact__last_name',
        'created_on',
        'date',
    )
    ordering = ('-date', '-created_on')
