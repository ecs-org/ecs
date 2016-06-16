from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q

from ecs.users.utils import user_flag_required


@user_flag_required('is_internal')
def autocomplete(request, queryset_name=None):
    term = request.GET.get('term', '')

    USER_QUERY = {
        'users': Q(),
        'internal-users': Q(profile__is_internal=True),
        'board-members': Q(
            groups__name__in=['EC-Board Member', 'EC-Executive Board Member']),
        'pki-users':
            Q(profile__is_internal=True) | Q(profile__is_omniscient_member=True),
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
