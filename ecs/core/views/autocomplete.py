from django.http import Http404, JsonResponse
from django.contrib.auth.models import User, Group
from django.db.models import Q, F, Value as V
from django.db.models.functions import Concat

from django_countries import countries

from ecs.core.models import MedicalCategory, ExpeditedReviewCategory
from ecs.users.utils import user_flag_required
from ecs.tasks.models import TaskType
from ecs.utils.security import readonly


@readonly()
def autocomplete(request, queryset_name=None):
    term = request.GET.get('term', '')

    if queryset_name == 'countries':
        results = [
            {'id': iso, 'text': '{} ({})'.format(name, iso)}
            for iso, name in countries
            if term.lower() in iso.lower() or term.lower() in name.lower()
        ]
    elif queryset_name == 'medical-categories':
        results = list(MedicalCategory.objects
            .annotate(text=Concat(F('name'), V(' ('), F('abbrev'), V(')')))
            .filter(text__icontains=term)
            .order_by('text')
            .values('id', 'text')
        )
    elif queryset_name == 'expedited-review-categories':
        results = list(ExpeditedReviewCategory.objects
            .annotate(text=Concat(F('name'), V(' ('), F('abbrev'), V(')')))
            .filter(text__icontains=term)
            .order_by('text')
            .values('id', 'text')
        )
    elif queryset_name == 'task-types':
        task_types = (TaskType.objects
            .order_by('workflow_node__uid', '-pk')
            .distinct('workflow_node__uid')
            .annotate(uid=F('workflow_node__uid'))
        )
        results = [
            {'id': tt.id, 'text': tt.trans_name} for tt in task_types
            if term.lower() in tt.trans_name.lower()
        ]
    else:
        return internal_autocomplete(request, queryset_name=queryset_name)

    return JsonResponse({'results': results})


@readonly()
@user_flag_required('is_internal')
def internal_autocomplete(request, queryset_name=None):
    term = request.GET.get('term', '')

    if queryset_name == 'groups':
        results = list(Group.objects
            .filter(name__icontains=term)
            .order_by('name')
            .annotate(text=F('name'))
            .values('id', 'text')
        )
        return JsonResponse({'results': results})

    USER_QUERY = {
        'users': Q(),
        'external-reviewers': Q(groups__name='External Reviewer'),
        'internal-users': Q(profile__is_internal=True),
        'board-members': Q(
            groups__name__in=['EC-Board Member', 'EC-Executive Board Group']),
    }

    users = (User.objects
        .filter(USER_QUERY[queryset_name], is_active=True)
        .select_related('profile')
        .order_by('first_name', 'last_name', 'email')
    )

    if term:
        q = Q()
        for bit in term.split():
            q &= (
                Q(first_name__icontains=bit) |
                Q(last_name__icontains=bit) |
                Q(email__icontains=bit) |
                Q(profile__title__icontains=bit)
            )
        users = users.filter(q)

    results = [{'id': u.id, 'text': '{} [{}]'.format(u, u.email)} for u in users]
    return JsonResponse({'results': results})
