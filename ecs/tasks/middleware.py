from django.conf import settings

from ecs.tasks.models import Task
from ecs.utils.lazy import LazyList


class RelatedTasksMiddleware(object):
    def _get_related_tasks(self, request):
        user_tasks = Task.objects.for_user(request.user).filter(closed_at__isnull=True).select_related('task_type')
        accepted_tasks = user_tasks.filter(assigned_to=request.user, accepted=True, deleted_at=None)
        for t in accepted_tasks:
            if request.path in t.get_final_urls():
                yield t

    def process_request(self, request):
        if not request.user.is_authenticated() or request.is_ajax() or \
            request.path.startswith(settings.STATIC_URL):
            return

        request.related_tasks = LazyList(self._get_related_tasks, request)
