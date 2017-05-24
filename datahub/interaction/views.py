from datahub.core.viewsets import CoreViewSetV1
from datahub.interaction.models import Interaction
from datahub.interaction.serializers import (
    InteractionSerializerRead,
    InteractionSerializerWrite,
)


class InteractionViewSetV1(CoreViewSetV1):
    """Interaction ViewSet."""

    read_serializer_class = InteractionSerializerRead
    write_serializer_class = InteractionSerializerWrite
    queryset = Interaction.objects.select_related(
        'interaction_type',
        'dit_adviser',
        'company',
        'contact'
    ).all()

    def get_additional_data(self, create):
        """Set dit_advisor to the user on model instance creation."""
        data = {}
        if create:
            data['dit_adviser'] = self.request.user
        return data
