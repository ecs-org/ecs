from django.conf import settings
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.checklists.models import Checklist
from ecs.communication.utils import send_system_message_template
from ecs.tasks.signals import task_declined
from ecs.users.utils import sudo
from ecs.meetings.models import Meeting
from ecs.billing.models import Price

register(Checklist)

@guard(model=Checklist)
def is_external_review_checklist(wf):
    return wf.data.blueprint.slug == 'external_review'

@guard(model=Checklist)
def checklist_review_review_failed(wf):
    return wf.data.status == 'review_fail'

class ExternalReview(Activity):
    class Meta:
        model = Checklist

    def is_repeatable(self):
        return True

    def is_reentrant(self):
        return True

    def is_locked(self):
        checklist = self.workflow.data
        return not checklist.is_complete

    def get_url(self):
        checklist = self.workflow.data
        blueprint_id = checklist.blueprint_id
        submission_form_id = checklist.submission.current_submission_form_id
        return reverse('ecs.core.views.submissions.checklist_review', kwargs={'submission_form_pk': submission_form_id, 'blueprint_pk': blueprint_id})

    def get_final_urls(self):
        checklist = self.workflow.data
        blueprint_id = checklist.blueprint_id
        return super().get_final_urls() + [
            reverse('ecs.core.views.submissions.checklist_review', kwargs={'submission_form_pk': sf, 'blueprint_pk': blueprint_id})
            for sf in self.workflow.data.submission.forms.values_list('pk', flat=True)
        ]

    def get_afterlife_url(self):
        c = self.workflow.data
        return '{0}#checklist_{1}_review_form'.format(reverse('view_submission', kwargs={'submission_pk': c.submission.pk}), c.pk)

    def receive_token(self, *args, **kwargs):
        c = self.workflow.data
        token = super().receive_token(*args, **kwargs)
        token.task.assign(c.user)
        if c.status == 'new':
            with sudo():
                meeting = Meeting.objects.filter(
                    timetable_entries__submission=c.submission, started=None
                ).order_by('start').first()
            price = Price.objects.get_review_price()
            url = reverse('ecs.tasks.views.do_task', kwargs={'task_pk': token.task.pk})
            send_system_message_template(c.user, _('Request for review'), 'checklists/external_reviewer_invitation.txt', {'task': token.task, 'meeting': meeting, 'price': price, 'ABSOLUTE_URL_PREFIX': settings.ABSOLUTE_URL_PREFIX, 'url': url}, submission=c.submission)
        return token

@receiver(post_save, sender=Checklist)
def unlock_external_review(sender, **kwargs):
    kwargs['instance'].workflow.unlock(ExternalReview)

# treat declined external review tasks as if the deadline was reached
@receiver(task_declined, sender=ExternalReview)
def external_review_declined(sender, **kwargs):
    task = kwargs['task']
    task.node_controller.progress(task.workflow_token, deadline=True)

class ExternalReviewReview(Activity):
    class Meta:
        model = Checklist

    def get_url(self):
        checklist = self.workflow.data
        submission_form_id = checklist.submission.current_submission_form_id
        return reverse('ecs.core.views.submissions.show_checklist_review', kwargs={'submission_form_pk': submission_form_id, 'checklist_pk': checklist.pk})

    def get_choices(self):
        return (
            ('review_ok', _('Publish')),
            ('review_fail', _('Send back to external Reviewer')),
            ('dropped', _('Drop')),
        )

    def pre_perform(self, choice):
        c = self.workflow.data
        c.status = choice
        c.save()
        if c.status == 'review_ok':
            if not c.pdf_document:
                c.render_pdf_document()
            presenting_parties = c.submission.current_submission_form.get_presenting_parties()
            presenting_parties.send_message(_('External Review'), 'checklists/external_review_publish.txt',
                {'checklist': c, 'ABSOLUTE_URL_PREFIX': settings.ABSOLUTE_URL_PREFIX},
                submission=c.submission)
        elif c.status == 'review_fail':
            send_system_message_template(c.user, _('Query regarding review'), 'checklists/external_review_declined.txt', None, submission=c.submission)
