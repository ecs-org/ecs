from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from ecs.workflow import Activity, guard, register
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, NotificationAnswer
from ecs.core.models import Submission

def _autostart_if(n, created):
    return n.submission_forms.exists()

for cls in (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification):
    register(cls, autostart_if=_autostart_if)


@guard(model=Notification)
def needs_executive_answer(wf):
    return Submission.objects.filter(forms__notifications=wf.data, is_amg=True).exists() and wf.data.type.executive_answer_required_for_amg


@guard(model=Notification)
def is_amendment(wf):
    return wf.data.type.diff
    

@guard(model=Notification)
def is_valid_amendment(wf):
    return wf.data.type.diff and wf.data.answer.valid


class EditNotificationAnswer(Activity):
    class Meta:
        model = Notification
    
    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})
        
    def get_final_urls(self):
        return super(EditNotificationAnswer, self).get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]
        
    def is_locked(self):
        try:
            return bool(self.workflow.data.answer)
        except NotificationAnswer.DoesNotExist:
            return False


class SignNotificationAnswer(Activity):
    class Meta:
        model = Notification


class DistributeNotificationAnswer(Activity):
    class Meta:
        model = Notification
        
    def get_url(self):
        return reverse('ecs.notifications.views.distribute_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})

