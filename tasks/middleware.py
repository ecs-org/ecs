# -*- coding: utf-8 -*-

from ecs.tasks.models import Task

class RelatedTasksMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        user_tasks = Task.objects.for_widget(request.user).filter(closed_at__isnull=True).select_related('task_type')
        accepted_tasks = user_tasks.filter(assigned_to=request.user, accepted=True, deleted_at=None)
        request.related_tasks =  [t for t in accepted_tasks if request.path in t.get_final_urls()]
