"""common RBAC serializers"""
from typing import Optional

from django.apps import apps
from django_filters.filters import CharFilter
from django_filters.filterset import FilterSet
from guardian.models import UserObjectPermission
from guardian.shortcuts import get_objects_for_user
from rest_framework.fields import SerializerMethodField
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from authentik.api.pagination import SmallerPagination
from authentik.rbac.api.rbac_assigned_by_users import UserObjectPermissionSerializer


class ExtraUserObjectPermissionSerializer(UserObjectPermissionSerializer):
    """User permission with additional object-related data"""

    app_label_verbose = SerializerMethodField()
    model_verbose = SerializerMethodField()

    object_description = SerializerMethodField()

    def get_app_label_verbose(self, instance: UserObjectPermission) -> str:
        return apps.get_app_config(instance.content_type.app_label).verbose_name

    def get_model_verbose(self, instance: UserObjectPermission) -> str:
        return apps.get_model(
            instance.content_type.app_label, instance.content_type.model
        )._meta.verbose_name

    def get_object_description(self, instance: UserObjectPermission) -> Optional[str]:
        app_label = instance.content_type.app_label
        model = instance.content_type.model
        model_class = apps.get_model(app_label, model)
        objects = get_objects_for_user(instance.user, f"{app_label}.view_{model}", model_class)
        obj = objects.first()
        if not obj:
            return None
        return str(obj)

    class Meta(UserObjectPermissionSerializer.Meta):
        fields = UserObjectPermissionSerializer.Meta.fields + [
            "app_label_verbose",
            "model_verbose",
            "object_description",
        ]


class UserPermissionFilter(FilterSet):
    """User-assigned permission filter"""

    username = CharFilter("user__username", required=True)


class UserPermissionViewSet(ListModelMixin, GenericViewSet):
    """Get a users's assigned object permissions"""

    serializer_class = ExtraUserObjectPermissionSerializer
    ordering = ["user__username"]
    pagination_class = SmallerPagination
    # The filtering is done in the filterset,
    # which has a required filter that does the heavy lifting
    queryset = UserObjectPermission.objects.select_related("content_type", "user").all()
    filterset_class = UserPermissionFilter
