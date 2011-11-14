# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from ecs.workflow import guard, Activity, register
from ecs.users.models import UserProfile


register(UserProfile, autostart_if=lambda p, created: p.start_workflow and not p.workflow)

@guard(model=UserProfile)
def is_approved(wf):
    return wf.data.is_approved_by_office

class UserApproval(Activity):
    class Meta:
        model = UserProfile

    def get_url(self):
        return reverse('ecs.users.views.approve', kwargs={'user_pk': self.workflow.data.user.pk})

