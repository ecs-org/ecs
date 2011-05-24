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

register(Submission, autostart_if=lambda s, created: bool(s.current_submission_form_id) and not s.workflow and not s.transient)
register(Vote)

@guard(model=Submission)
def is_acknowledged(wf):
    return wf.data.current_submission_form.acknowledged

@guard(model=Submission)
def is_retrospective_thesis(wf):
    # information provided by the presenter
    retrospective = bool(wf.data.current_submission_form.project_type_retrospective)
    thesis = wf.data.current_submission_form.project_type_education_context is not None

    # information provided by the categorization review
    if not wf.data.retrospective is None:
        retrospective = bool(wf.data.retrospective)
    if not wf.data.thesis is None:
        thesis = bool(wf.data.thesis)

    return retrospective and thesis

@guard(model=Submission)
def has_b2vote(wf):
    sf = wf.data.current_submission_form
    if sf.current_pending_vote:
        return sf.current_pending_vote.result == '2'
    if sf.current_published_vote:
        return sf.current_published_vote.result == '2'
    return False

@guard(model=Vote)
def is_executive_vote_review_required(wf):
    return wf.data.executive_review_required


@guard(model=Vote)
def is_final(wf):
    return wf.data.is_final
    
@guard(model=Vote)
def is_b2upgrade(wf):
    previous_vote = wf.data.submission_form.votes.filter(pk__lt=wf.data.pk).order_by('-pk')[:1]
    return wf.data.activates and previous_vote and previous_vote[0].result == '2'

@guard(model=Submission)
def is_expedited(wf):
    return wf.data.expedited and wf.data.expedited_review_categories.count()

@guard(model=Submission)
def has_expedited_recommendation(wf):
    answer = ChecklistAnswer.objects.get(checklist__submission=wf.data, question__blueprint__slug='expedited_review', question__number='1')
    return bool(answer.answer)

@guard(model=Submission)
def has_thesis_recommendation(wf):
    answer = ChecklistAnswer.objects.get(checklist__submission=wf.data, question__blueprint__slug='thesis_review', question__number='1')
    return bool(answer.answer)

@guard(model=Submission)
def needs_external_review(wf):
    with sudo():
        external_review_exists = Task.objects.for_data(wf.data).filter(assigned_to=wf.data.external_reviewer_name, task_type__workflow_node__uid='external_review', deleted_at__isnull=True).exists()
    return wf.data.external_reviewer and not external_review_exists

@guard(model=Submission)
def needs_insurance_review(wf):
    return wf.data.insurance_review_required

@guard(model=Submission)
def needs_gcp_review(wf):
    return wf.data.gcp_review_required

@guard(model=Submission)
def needs_boardmember_review(wf):
    return is_retrospective_thesis(wf) or is_expedited(wf) or wf.data.medical_categories.count()

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
            send_system_message_template(sf.presenter, _('Study acknowledged'), 'submissions/acknowledge_message.txt', None, submission=s)
        else:
            send_system_message_template(sf.presenter, _('Study declined'), 'submissions/decline_message.txt', None, submission=s)

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


class B2VoteReview(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return reverse('ecs.core.views.b2_vote_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form.pk})

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
        if is_acknowledged(self.workflow) and s.timetable_entries.count() == 0 and not is_expedited(self.workflow):
            # schedule submission for the next schedulable meeting
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.add_entry(submission=s, duration=timedelta(minutes=7.5))

        if s.external_reviewer:
            send_system_message_template(s.external_reviewer_name, _('External Review Invitation'), 'submissions/external_reviewer_invitation.txt', None, submission=s)
        for add_rev in s.additional_reviewers.all():
            send_system_message_template(add_rev, _('Additional Review Invitation'), 'submissions/additional_reviewer_invitation.txt', None, submission=s)

class ThesisCategorizationReview(_CategorizationReviewBase):
    class Meta:
        model = Submission

    def pre_perform(self, choice):
        s = self.workflow.data
        if s.external_reviewer:
            send_system_message_template(s.external_reviewer_name, _('External Review Invitation'), 'submissions/external_reviewer_invitation.txt', None, submission=s)
        for add_rev in s.additional_reviewers.all():
            send_system_message_template(add_rev, _('Additional Review Invitation'), 'submissions/additional_reviewer_invitation.txt', None, submission=s)

class PaperSubmissionReview(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})


class ChecklistReview(Activity):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint
        
    def is_reentrant(self):
        return False
        
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


# XXX: This could be done without a Meta-class and without the additional signal handler if `ecs.workflow` properly supported activity inheritance. (FMD3)
class ExternalChecklistReview(ChecklistReview):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint
        
    def is_reentrant(self):
        return True

    def receive_token(self, *args, **kwargs):
        token = super(ExternalChecklistReview, self).receive_token(*args, **kwargs)
        token.task.assign(self.workflow.data.external_reviewer_name)
        return token

def unlock_external_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExternalChecklistReview)
post_save.connect(unlock_external_review, sender=Checklist)

# treat declined external review tasks as if the deadline was reached
def external_review_declined(sender, **kwargs):
    task = kwargs['task']
    task.node_controller.progress(task.workflow_token, deadline=True)
task_declined.connect(external_review_declined, sender=ExternalChecklistReview)


# XXX: This could be done without a Meta-class and without the additional signal handler if `ecs.workflow` properly supported activity inheritance. (FMD3)
class ThesisRecommendationReview(ChecklistReview):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint

    def is_reentrant(self):
        return True

    def pre_perform(self, choice):
        s = self.workflow.data
        if has_thesis_recommendation(self.workflow) and s.timetable_entries.count() == 0:
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.retrospective_thesis_submissions.add(s)

def unlock_thesis_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ThesisRecommendationReview)
post_save.connect(unlock_thesis_recommendation_review, sender=Checklist)

class ExpeditedRecommendation(ChecklistReview):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint

    def receive_token(self, *args, **kwargs):
        token = super(ExpeditedRecommendation, self).receive_token(*args, **kwargs)
        for cat in self.workflow.data.expedited_review_categories.all():
            token.task.expedited_review_categories.add(cat)
        return token

def unlock_expedited_recommendation(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExpeditedRecommendation)
post_save.connect(unlock_expedited_recommendation, sender=Checklist)

class ExpeditedRecommendationReview(ChecklistReview):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint

    def is_reentrant(self):
        return True

    def pre_perform(self, choice):
        s = self.workflow.data
        if has_expedited_recommendation(self.workflow) and s.timetable_entries.count() == 0:
            meeting = Meeting.objects.next_schedulable_meeting(s)
            meeting.expedited_submissions.add(s)

def unlock_expedited_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExpeditedRecommendationReview)
post_save.connect(unlock_expedited_recommendation_review, sender=Checklist)


@guard(model=Submission)
def needs_external_review(wf):
    from ecs.tasks.models import Task
    with sudo():
        external_review_exists = Task.objects.for_data(wf.data).filter(assigned_to=wf.data.external_reviewer_name, task_type__workflow_node__uid='external_review', deleted_at__isnull=True).exists()
    return wf.data.external_reviewer and not external_review_exists


class AdditionalReviewSplit(Generic):
    class Meta:
        model = Submission

    def emit_token(self, *args, **kwargs):
        tokens = []
        for user in self.workflow.data.additional_reviewers.all():
            with sudo():
                additional_review_exists = Task.objects.for_data(self.workflow.data).filter(assigned_to=user, task_type__workflow_node__uid='additional_review', deleted_at__isnull=True).exists()
            if additional_review_exists:
                continue
            for token in super(AdditionalReviewSplit, self).emit_token(*args, **kwargs):
                token.task.assign(user)
                tokens.append(token)
        return tokens

# XXX: This could be done without a Meta-class and without the additional signal handler if `ecs.workflow` properly supported activity inheritance. (FMD3)
class AdditionalChecklistReview(ChecklistReview):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint
        
    def is_reentrant(self):
        return True

def unlock_additional_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(AdditionalChecklistReview)
post_save.connect(unlock_additional_review, sender=Checklist)

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
        vote.published_at = datetime.now()
        vote.save()

