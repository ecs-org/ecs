from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from ecs.workflow import Activity, guard, register
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, NotificationAnswer
from ecs.core.models import Submission

for cls in (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification):
    register(cls, autostart_if=lambda n, created: n.submission_forms.exists() and not n.workflow.workflows.exists())


@guard(model=Notification)
def needs_executive_review(wf):
    return wf.data.needs_executive_review

@guard(model=Notification)
def is_susar(wf):
    return wf.data.type.name == u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)"

@guard(model=Notification)
def is_report(wf):
    return wf.data.type.name == u"Zwischenbericht" or wf.data.type.name == u"Abschlussbericht"

@guard(model=Notification)
def is_amendment(wf):
    return wf.data.type.name == u"Amendment"

class InitialNotificationReview(Activity):
    class Meta:
        model = Notification

    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super(InitialNotificationReview, self).get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]

    def get_choices(self):
        return (
            (False, _('Notification Group Review')),
            (True, _('Executive Review')),
        )

    def pre_perform(self, choice):
        n = self.workflow.data
        n.needs_executive_review = choice
        n.save()

class EditNotificationAnswer(Activity):
    class Meta:
        model = Notification
    
    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})
        
    def get_final_urls(self):
        return super(EditNotificationAnswer, self).get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]

class SignNotificationAnswer(Activity):
    class Meta:
        model = Notification


class DistributeNotificationAnswer(Activity):
    class Meta:
        model = Notification
        
    def get_url(self):
        return reverse('ecs.notifications.views.distribute_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})
