from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.notifications.models import (
    Notification, CompletionReportNotification, ProgressReportNotification,
    SafetyNotification, CenterCloseNotification, NOTIFICATION_MODELS,
)
from ecs.notifications.signals import on_safety_notification_review


for cls in NOTIFICATION_MODELS:
    register(cls, autostart_if=lambda n, created: n.submission_forms.exists() and not n.workflow.workflows.exists())


@guard(model=Notification)
def is_susar(wf):
    return SafetyNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_report(wf):
    return CompletionReportNotification.objects.filter(pk=wf.data.pk).exists() or ProgressReportNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_center_close(wf):
    return CenterCloseNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_amendment(wf):
    return wf.data.type.name == "Amendment"

@guard(model=Notification)
def needs_further_review(wf):
    return wf.data.answer.needs_further_review

@guard(model=Notification)
def is_rejected_and_final(wf):
    return (wf.data.answer.is_rejected and wf.data.answer.is_final_version)

class BaseNotificationReview(Activity):
    def get_url(self):
        return reverse('ecs.notifications.views.edit_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super().get_final_urls() + [reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': self.workflow.data.pk})]


class InitialAmendmentReview(BaseNotificationReview):
    class Meta:
        model = Notification
        
    def get_choices(self):
        return (
            (True, _('Acknowledge')),
            (False, _('Reject')),
        )

    def pre_perform(self, choice):
        if not choice:
            answer = self.workflow.data.answer
            answer.is_valid = True
            answer.is_rejected = True
            answer.is_final_version = True
            answer.save()


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
        answer.save()


class SimpleNotificationReview(BaseNotificationReview):
    class Meta:
        model = Notification


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

    def get_choices(self):
        return (
            (True, 'ok'),
            (False, 'pushback'),
        )

    def get_url(self):
        return reverse('ecs.notifications.views.notification_answer_sign', kwargs={'notification_pk': self.workflow.data.pk})

    def pre_perform(self, choice):
        answer = self.workflow.data.answer
        if choice:
            answer.distribute()

class AutoDistributeNotificationAnswer(Generic):
    class Meta:
        model = Notification

    def handle_token(self, token):
        answer = self.workflow.data.answer
        answer.distribute()
        answer.render_pdf() # xxx need to render pdf after distribute, to have new vote extension date already set
        super().handle_token(token)
