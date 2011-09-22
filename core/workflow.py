# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.users.utils import get_current_user, sudo
from ecs.core.models import Submission, ChecklistBlueprint, Checklist, ChecklistAnswer, Vote
from ecs.meetings.models import Meeting
from ecs.tasks.signals import task_accepted, task_declined
from ecs.tasks.models import Task
from ecs.communication.utils import send_system_message_template
from ecs.core.models.submissions import SUBMISSION_TYPE_MULTICENTRIC_LOCAL

register(Submission, autostart_if=lambda s, created: bool(s.current_submission_form_id) and not s.workflow and not s.transient)
register(Vote)
register(Checklist)

@guard(model=Submission)
def is_acknowledged(wf):
    return wf.data.current_submission_form.acknowledged

@guard(model=Submission)
def is_acknowledged_and_localec(wf):
    return is_acknowledged(wf) and is_localec(wf)

@guard(model=Submission)
def is_acknowledged_and_not_localec(wf):
    return is_acknowledged(wf) and not is_localec(wf)

@guard(model=Submission)
def is_thesis(wf):
    return bool(Submission.objects.thesis().filter(pk=wf.data.pk).count()) and not is_expedited(wf)

@guard(model=Submission)
def is_retrospective_thesis(wf):
    return bool(Submission.objects.retrospective_thesis().filter(pk=wf.data.pk).count()) and not is_expedited(wf)

@guard(model=Submission)
def is_expedited(wf):
    return wf.data.expedited and wf.data.expedited_review_categories.count()

@guard(model=Submission)
def is_localec(wf):
    return wf.data.current_submission_form.submission_type == SUBMISSION_TYPE_MULTICENTRIC_LOCAL

@guard(model=Submission)
def is_expedited_or_retrospective_thesis(wf):
    return is_expedited(wf) or is_retrospective_thesis(wf)

@guard(model=Vote)
def is_executive_vote_review_required(wf):
    return wf.data.executive_review_required


@guard(model=Vote)
def is_final(wf):
    return wf.data.is_final

@guard(model=Vote)
def is_b2(wf):
    return wf.data.result == '2'

@guard(model=Vote)
def is_b2upgrade(wf):
    previous_vote = wf.data.submission_form.votes.filter(pk__lt=wf.data.pk).order_by('-pk')[:1]
    return wf.data.activates and previous_vote and previous_vote[0].result == '2'

@guard(model=Submission)
def has_expedited_recommendation(wf):
    answer = ChecklistAnswer.objects.get(checklist__submission=wf.data, question__blueprint__slug='expedited_review', question__number='1')
    return bool(answer.answer)

@guard(model=Submission)
def has_thesis_recommendation(wf):
    answer = ChecklistAnswer.objects.get(checklist__submission=wf.data, question__blueprint__slug='thesis_review', question__number='1')
    return bool(answer.answer)

@guard(model=Submission)
def needs_insurance_review(wf):
    return wf.data.insurance_review_required

@guard(model=Submission)
def needs_gcp_review(wf):
    return wf.data.gcp_review_required

@guard(model=Submission)
def needs_legal_and_patient_review(wf):
    return wf.data.legal_and_patient_review_required

@guard(model=Submission)
def needs_statistical_review(wf):
    return wf.data.statistical_review_required

@guard(model=Checklist)
def is_external_review_checklist(wf):
    return wf.data.blueprint.slug == 'external_review'

@guard(model=Checklist)
def checklist_review_review_failed(wf):
    return wf.data.status == 'review_fail'

class InitialReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})

    def get_choices(self):
        return (
            (True, _('Acknowledge')),
            (False, _('Reject')),
        )

    def pre_perform(self, choice):
        s = self.workflow.data
        sf = s.current_submission_form
        sf.acknowledged = choice
        sf.save()

        if sf.acknowledged:
            send_system_message_template(sf.presenter, _('Submission accepted'), 'submissions/acknowledge_message.txt', None, submission=s)
        else:
            send_system_message_template(sf.presenter, _('Submission not accepted'), 'submissions/decline_message.txt', None, submission=s)

class Resubmission(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.copy_latest_submission_form', kwargs={'submission_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super(Resubmission, self).get_final_urls() + [
            reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': sf})
            for sf in self.workflow.data.forms.values_list('pk', flat=True)
        ]

    def receive_token(self, *args, **kwargs):
        token = super(Resubmission, self).receive_token(*args, **kwargs)
        token.task.assign(self.workflow.data.current_submission_form.presenter)
        return token

class _CategorizationReviewBase(Activity):
    class Meta:
        model = Submission

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.categorization_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form.pk})

class CategorizationReview(_CategorizationReviewBase):
    class Meta:
        model = Submission

    def pre_perform(self, choice):
        s = self.workflow.data
        is_special = is_expedited(self.workflow) or is_retrospective_thesis(self.workflow) or is_localec(self.workflow)
        if is_acknowledged(self.workflow) and s.timetable_entries.count() == 0 and not is_special:
            # schedule submission for the next schedulable meeting
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.add_entry(submission=s, duration=timedelta(minutes=7.5))

        # create external review checklists
        blueprint = ChecklistBlueprint.objects.get(slug='external_review')
        for user in s.external_reviewers.all():
            checklist, created = Checklist.objects.get_or_create(blueprint=blueprint, submission=s, user=user)
            if created:
                for question in blueprint.questions.order_by('text'):
                    ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)

class ThesisCategorizationReview(_CategorizationReviewBase):
    class Meta:
        model = Submission

    def pre_perform(self, choice):
        s = self.workflow.data

class PaperSubmissionReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})


class ChecklistReview(Activity):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint

    def is_repeatable(self):
        return True

    def is_reentrant(self):
        return True

    def is_locked(self):
        blueprint = self.node.data
        lookup_kwargs = {'blueprint': blueprint}
        if blueprint.multiple:
            lookup_kwargs['user'] = get_current_user()
        try:
            checklist = self.workflow.data.checklists.get(**lookup_kwargs)
        except Checklist.DoesNotExist:
            return False
        return not checklist.is_complete

    def get_url(self):
        blueprint = self.node.data
        submission_form = self.workflow.data.current_submission_form
        return reverse('ecs.core.views.checklist_review', kwargs={'submission_form_pk': submission_form.pk, 'blueprint_pk': blueprint.pk})

def unlock_checklist_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ChecklistReview)
post_save.connect(unlock_checklist_review, sender=Checklist)

class NonRepeatableChecklistReview(ChecklistReview):
    def is_repeatable(self):
        return False

    def is_reentrant(self):
        return False

def unlock_non_repeatable_checklist_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(NonRepeatableChecklistReview)
post_save.connect(unlock_checklist_review, sender=Checklist)

class BoardMemberReview(ChecklistReview):
    def is_reentrant(self):
        return True

def unlock_boardmember_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(BoardMemberReview)
post_save.connect(unlock_boardmember_review, sender=Checklist)


# XXX: This could be done without the additional signal handler if `ecs.workflow` properly supported activity inheritance. (FMD3)
class ThesisRecommendationReview(NonRepeatableChecklistReview):
    def is_reentrant(self):
        return True

    def pre_perform(self, choice):
        s = self.workflow.data
        if has_thesis_recommendation(self.workflow) and s.timetable_entries.count() == 0:
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.add_entry(submission=s, duration=timedelta(seconds=0), visible=False)

def unlock_thesis_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ThesisRecommendationReview)
post_save.connect(unlock_thesis_recommendation_review, sender=Checklist)

class ExpeditedRecommendation(NonRepeatableChecklistReview):
    def receive_token(self, *args, **kwargs):
        token = super(ExpeditedRecommendation, self).receive_token(*args, **kwargs)
        for cat in self.workflow.data.expedited_review_categories.all():
            token.task.expedited_review_categories.add(cat)
        return token

def unlock_expedited_recommendation(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExpeditedRecommendation)
post_save.connect(unlock_expedited_recommendation, sender=Checklist)

class ExpeditedRecommendationReview(NonRepeatableChecklistReview):
    def is_reentrant(self):
        return True

    def pre_perform(self, choice):
        s = self.workflow.data
        if has_expedited_recommendation(self.workflow) and s.timetable_entries.count() == 0:
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.add_entry(submission=s, duration=timedelta(seconds=0), visible=False)

def unlock_expedited_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExpeditedRecommendationReview)
post_save.connect(unlock_expedited_recommendation_review, sender=Checklist)


class LocalEcRecommendationReview(NonRepeatableChecklistReview):
    def is_reentrant(self):
        return True

    def pre_perform(self, choice):
        s = self.workflow.data
        if s.timetable_entries.count() == 0:
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.add_entry(submission=s, duration=timedelta(seconds=0), visible=False)

def unlock_localec_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(LocalEcRecommendationReview)
post_save.connect(unlock_localec_recommendation_review, sender=Checklist)

class VoteFinalization(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})


class VoteReview(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.vote_review', kwargs={'submission_form_pk': self.workflow.data.submission_form_id})


class VoteSigning(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.vote_sign', kwargs={'vote_pk': self.workflow.data.pk})


class VotePublication(Activity):
    class Meta:
        model = Vote

    def pre_perform(self, choice):
        vote = self.workflow.data
        vote.publish()

class VoteB2Review(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.submission_form.pk})

    def get_choices(self):
        return (
            ('1', _('B1')),
            ('3', _('B3')),
        )

    def pre_perform(self, choice):
        from ecs.core.models.voting import PERMANENT_VOTE_RESULTS
        sf = self.workflow.data.submission_form
        new_vote = Vote.objects.create(submission_form=sf, result=choice)
        if new_vote.result in PERMANENT_VOTE_RESULTS:
            # abort all tasks
            with sudo():
                open_tasks = Task.objects.for_data(sf.submission).filter(deleted_at__isnull=True, closed_at=None)
                for task in open_tasks:
                    task.deleted_at = datetime.now()
                    task.save()
        if choice == '3':
            meeting = Meeting.objects.next_schedulable_meeting(sf.submission)
            # only works for normal studies (no thesis lane, etc.)
            meeting.add_entry(submission=sf.submission, duration=timedelta(minutes=7.5))

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
        blueprint = checklist.blueprint
        submission_form = checklist.submission.current_submission_form
        return reverse('ecs.core.views.checklist_review', kwargs={'submission_form_pk': submission_form.pk, 'blueprint_pk': blueprint.pk})

    def receive_token(self, *args, **kwargs):
        c = self.workflow.data
        token = super(ExternalReview, self).receive_token(*args, **kwargs)
        token.task.assign(c.user)
        if c.status == 'new':
            send_system_message_template(c.user, _('External Review Invitation'), 'submissions/external_reviewer_invitation.txt', None, submission=c.submission)
        return token

def unlock_external_review(sender, **kwargs):
    kwargs['instance'].workflow.unlock(ExternalReview)
post_save.connect(unlock_external_review, sender=Checklist)

# treat declined external review tasks as if the deadline was reached
def external_review_declined(sender, **kwargs):
    task = kwargs['task']
    task.node_controller.progress(task.workflow_token, deadline=True)
task_declined.connect(external_review_declined, sender=ExternalReview)

class ExternalReviewReview(Activity):
    class Meta:
        model = Checklist

    def get_url(self):
        checklist = self.workflow.data
        submission_form = checklist.submission.current_submission_form
        return reverse('ecs.core.views.show_checklist_review', kwargs={'submission_form_pk': submission_form.pk, 'checklist_pk': checklist.pk})

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
            c.render_pdf()
            presenting_users = set([p.user for p in c.submission.current_submission_form.get_presenting_parties() if p.user])
            for u in presenting_users:
                send_system_message_template(u, _('External Review'), 'submissions/external_review_publish.txt', {'checklist': c}, submission=c.submission)
        elif c.status == 'review_fail':
            send_system_message_template(c.user, _('External Review Declined'), 'submissions/external_review_declined.txt', None, submission=c.submission)
