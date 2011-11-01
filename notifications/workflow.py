from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, SafetyNotification
from ecs.notifications.signals import on_safety_notification_review

NOTIFICATION_MODELS = (Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification, SafetyNotification)

for cls in NOTIFICATION_MODELS:
    register(cls, autostart_if=lambda n, created: n.submission_forms.exists() and not n.workflow.workflows.exists())


@guard(model=Notification)
def needs_executive_review(wf):
    return wf.data.needs_executive_review

@guard(model=Notification)
def is_susar(wf):
    return SafetyNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_report(wf):
    return wf.data.type.name == u"Zwischenbericht" or wf.data.type.name == u"Abschlussbericht"

@guard(model=Notification)
def is_amendment(wf):
    return wf.data.type.name == u"Amendment"
    
@guard(model=Notification)
def is_rejected(wf):
    return wf.data.is_rejected
    
@guard(model=Notification)
def needs_further_review(wf):
    return wf.data.answer.needs_further_review


class BaseNotificationReview(Activity):
    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super(BaseNotificationReview, self).get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]


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
        n.new_submission_form.is_acknowledged = True
        n.new_submission_form.save()
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
        answer.is_valid = choice
        answer.review_count += 1
        answer.save()


class SafetyNotificationReview(Activity):
    class Meta:
        model = Notification

    def get_url(self):
        return reverse('ecs.notifications.views.view_notification', kwargs={'notification_pk': self.workflow.data.pk})
        
    def pre_perform(self, choice):
        notification = self.workflow.data
        on_safety_notification_review.send(type(notification), notification=notification)


class SignNotificationAnswer(Activity):
    class Meta:
        model = Notification
    
    def get_url(self): # FIXME
        return reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})


class AutoDistributeNotificationAnswer(Generic):
    class Meta:
        model = Notification

    def handle_token(self, token):
        self.workflow.data.answer.distribute()
        super(AutoDistributeNotificationAnswer, self).handle_token(token)
