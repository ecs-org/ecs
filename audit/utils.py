from django.contrib.contenttypes.models import ContentType
from ecs.audit.models import AuditTrail


def get_versions(obj):
    return AuditTrail.objects.filter(object_id=obj.pk, content_type=ContentType.objects.get_for_model(type(obj)))


def get_version_number(obj):
    return get_versions(obj).count()

