from datetime import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, NotificationAnswer
from ecs.core.models import Submission

NOTIFICATION_MODELS = (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification)

for cls in NOTIFICATION_MODELS:
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
    
@guard(model=Notification)
def is_rejected(wf):
    return wf.data.rejected
    
@guard(model=Notification)
def needs_further_review(wf):
    return wf.data.answer.needs_further_review


class BaseNotificationReview(Activity):
    def is_locked(self):
        try:
            return not self.workflow.data.answer
        except NotificationAnswer.DoesNotExist:
            return True

    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super(BaseNotificationReview, self).get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]


def unlock_notification_review(sender, **kwargs):
    notification = kwargs['instance'].notification
    for model in NOTIFICATION_MODELS:
        try:
            n = model.objects.get(pk=notification.pk)
            n.workflow.unlock(InitialNotificationReview)
            n.workflow.unlock(InitialAmendmentReview)
            n.workflow.unlock(EditNotificationAnswer)
        except model.DoesNotExist:
            pass
post_save.connect(unlock_notification_review, sender=NotificationAnswer)


class InitialNotificationReview(BaseNotificationReview):
    class Meta:
        model = Notification


class InitialAmendmentReview(InitialNotificationReview):
    class Meta:
        model = Notification
        
    def get_choices(self):
        return (
            (False, _('Notification Group Review')),
            (True, _('Executive Review')),
        )

    def pre_perform(self, choice):
        n = self.workflow.data
        n.needs_executive_review = choice
        n.save()


class EditNotificationAnswer(BaseNotificationReview):
    class Meta:
        model = Notification
    
    def get_choices(self):
        return (
            (True, _('Ready')),
            (False, _('Needs further review')),
        )
    
    def pre_perform(self, choice):
        answer = self.workflow.data.answer
        answer.valid = choice
        answer.review_count += 1
        answer.save()


class SignNotificationAnswer(Activity):
    class Meta:
        model = Notification


class AutoDistributeNotificationAnswer(Generic):
    class Meta:
        model = Notification

    def handle_token(self, token):
        self.workflow.data.answer.distribute()
        super(AutoDistributeNotificationAnswer, self).handle_token(token)
