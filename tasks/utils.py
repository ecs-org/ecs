from django.http import Http404
from django.contrib.contenttypes.models import ContentType


def has_task(user, activities, obj, data=None):
    tokens = obj.workflow.tokens.filter(node__node_type__in=[a._meta.node_type for a in activities], consumed_at=None)
    if data:
        tokens = tokens.filter(node__data_id=data.pk, node__data_ct=ContentType.objects.get_for_model(type(data)))
    return tokens.exists()
