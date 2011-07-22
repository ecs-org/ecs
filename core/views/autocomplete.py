from django.http import Http404, HttpResponse
from django.utils import simplejson
from django.contrib.auth.models import User, Group

from ecs.utils.countries.models import Country
from ecs.core.models import MedicalCategory, ExpeditedReviewCategory
from ecs.users.utils import user_flag_required
from ecs.tasks.models import TaskType

AUTOCOMPLETE_QUERYSETS = {
    'countries': lambda: [(c.pk, "%s (%s)" % (c.printable_name, c.iso), c.printable_name) for c in Country.objects.order_by('name')],
    'medical_categories': lambda: [(str(c.pk), "%s (%s)" % (c.name, c.abbrev), c.name) for c in MedicalCategory.objects.order_by('name')],
    'expedited_review_categories': lambda: [(str(c.pk), "%s (%s)" % (c.name, c.abbrev), c.name) for c in ExpeditedReviewCategory.objects.order_by('name')],
    'groups': lambda: [(str(g.pk), g.name, g.name) for g in Group.objects.order_by('name')],
    'task_types': lambda: [(str(tt.pk), tt.trans_name, tt.trans_name) for tt in TaskType.objects.order_by('name')],
}

INTERNAL_AUTOCOMPLETE_QUERYSETS = {
    'users': lambda: [(str(u.pk), '{0} [{1}]'.format(u, u.email), unicode(u)) for u in User.objects.order_by('first_name', 'last_name', 'email')],
    'external_reviewers': lambda: [(str(u.pk), '{0} [{1}]'.format(u, u.email), unicode(u)) for u in User.objects.filter(ecs_profile__external_review=True).order_by('first_name', 'last_name', 'email')],
}

def autocomplete(request, queryset_name=None):
    try:
        result = AUTOCOMPLETE_QUERYSETS[queryset_name]()
    except KeyError:
        raise Http404
    return HttpResponse(simplejson.dumps(result), content_type='application/json')

@user_flag_required('internal')
def internal_autocomplete(request, queryset_name=None):
    try:
        result = INTERNAL_AUTOCOMPLETE_QUERYSETS[queryset_name]()
    except KeyError:
        raise Http404
    return HttpResponse(simplejson.dumps(result), content_type='application/json')
