from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from datahub.company.serializers import AdviserSerializer


@api_view()
@permission_classes([IsAuthenticated])
def who_am_i(request):
    """Return the current user. This view is behind a login."""
    serializer = AdviserSerializer(request.user)
    return Response(data=serializer.data)
