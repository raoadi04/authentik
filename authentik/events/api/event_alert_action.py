"""EventAlertAction API Views"""
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from authentik.events.models import EventAlertAction


class EventAlertActionSerializer(ModelSerializer):
    """EventAlertAction Serializer"""

    class Meta:

        model = EventAlertAction
        fields = [
            "pk",
            "name",
        ]


class EventAlertActionViewSet(ModelViewSet):
    """EventAlertAction Viewset"""

    queryset = EventAlertAction.objects.all()
    serializer_class = EventAlertActionSerializer
