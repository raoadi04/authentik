"""User Delete Stage API Views"""
from rest_framework.viewsets import ModelViewSet

from authentik.flows.api.stages import StageSerializer
from authentik.stages.user_delete.models import UserDeleteStage


class UserDeleteStageSerializer(StageSerializer):
    """UserDeleteStage Serializer"""

    class Meta:

        model = UserDeleteStage
        fields = StageSerializer.Meta.fields


from authentik.core.api.used_by import UsedByMixin


class UserDeleteStageViewSet(UsedByMixin, ModelViewSet):
    """UserDeleteStage Viewset"""

    queryset = UserDeleteStage.objects.all()
    serializer_class = UserDeleteStageSerializer
