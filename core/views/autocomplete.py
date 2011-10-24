from django.http import Http404, HttpResponse
from django.utils import simplejson
from django.contrib.auth.models import User, Group

from ecs.utils.countries.models import Country
from ecs.core.models import MedicalCategory, ExpeditedReviewCategory
from ecs.users.utils import user_flag_required
from ecs.tasks.models import TaskType

def _get_task_types():
    uids = TaskType.objects.values_list('workflow_node__uid', flat=True).distinct()
    task_types = []
    for uid in uids:
        tt = TaskType.objects.filter(workflow_node__uid=uid).order_by('-pk')[0]
        task_types.append((uid, tt.trans_name, tt.trans_name,))
    return task_types

AUTOCOMPLETE_QUERYSETS = {
    'countries': lambda: [(c.pk, u"%s (%s)" % (c.printable_name, c.iso), c.printable_name) for c in Country.objects.order_by('name')],
    'medical_categories': lambda: [(str(c.pk), u"%s (%s)" % (c.name, c.abbrev), c.name) for c in MedicalCategory.objects.order_by('name')],
    'expedited_review_categories': lambda: [(str(c.pk), u"%s (%s)" % (c.name, c.abbrev), c.name) for c in ExpeditedReviewCategory.objects.order_by('name')],
    'task_types': _get_task_types,
}

INTERNAL_AUTOCOMPLETE_QUERYSETS = {
    'users': lambda: [(str(u.pk), u'{0} [{1}]'.format(u, u.email), unicode(u)) for u in User.objects.order_by('first_name', 'last_name', 'email')],
    'groups': lambda: [(str(g.pk), g.name, g.name) for g in Group.objects.order_by('name')],
}

def autocomplete(request, queryset_name=None):
    try:
        result = AUTOCOMPLETE_QUERYSETS[queryset_name]()
    except KeyError:
        raise Http404
    return HttpResponse(simplejson.dumps(result), content_type='application/json')

@user_flag_required('is_internal')
def internal_autocomplete(request, queryset_name=None):
    try:
        result = INTERNAL_AUTOCOMPLETE_QUERYSETS[queryset_name]()
    except KeyError:
        raise Http404
    return HttpResponse(simplejson.dumps(result), content_type='application/json')
