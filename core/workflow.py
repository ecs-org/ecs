# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.users.utils import get_current_user, sudo
from ecs.core.models import Submission
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_LOCALEC
from ecs.core.signals import on_initial_review, on_initial_thesis_review, on_categorization_review, on_b2_upgrade
from ecs.checklists.models import ChecklistBlueprint, Checklist, ChecklistAnswer
from ecs.checklists.utils import get_checklist_answer, get_checklist_comment
from ecs.tasks.models import Task, TaskType
from ecs.tasks.utils import block_if_task_exists
from ecs.votes.models import Vote
from ecs.meetings import signals as meeting_signals
from ecs.utils import connect

register(Submission, autostart_if=lambda s, created: bool(s.current_submission_form_id) and not s.workflow and not s.is_transient)

##########################
# acknowledgement guards #
##########################
@guard(model=Submission)
def is_acknowledged(wf):
    return wf.data.newest_submission_form.is_acknowledged

@guard(model=Submission)
def is_initial_submission(wf):
    return wf.data.forms.filter(is_acknowledged=True).count() == 1

@guard(model=Submission)
def is_acknowledged_and_initial_submission(wf):
    return is_acknowledged(wf) and is_initial_submission(wf)

###############
# lane guards #
###############
@guard(model=Submission)
def is_retrospective_thesis(wf):
    return wf.data.workflow_lane == SUBMISSION_LANE_RETROSPECTIVE_THESIS

@guard(model=Submission)
def is_expedited(wf):
    return wf.data.workflow_lane == SUBMISSION_LANE_EXPEDITED

@guard(model=Submission)
def is_localec(wf):
    return wf.data.workflow_lane == SUBMISSION_LANE_LOCALEC

@guard(model=Submission)
def is_expedited_or_retrospective_thesis(wf):
    return is_expedited(wf) or is_retrospective_thesis(wf)

#########################
# recommendation guards #
#########################
@guard(model=Submission)
def has_expedited_recommendation(wf):
    return bool(get_checklist_answer(wf.data, 'expedited_review', 1))

@guard(model=Submission)
def has_thesis_recommendation(wf):
    return bool(get_checklist_answer(wf.data, 'thesis_review', 1))

@guard(model=Submission)
def has_localec_recommendation(wf):
    return bool(get_checklist_answer(wf.data, 'localec_review', 1))

#################
# review guards #
#################
@guard(model=Submission)
@block_if_task_exists('insurance_review')
def needs_insurance_review(wf):
    return wf.data.insurance_review_required

@guard(model=Submission)
@block_if_task_exists('statistical_review')
def needs_statistical_review(wf):
    return wf.data.statistical_review_required

@guard(model=Submission)
@block_if_task_exists('legal_and_patient_review')
def needs_legal_and_patient_review(wf):
    return wf.data.legal_and_patient_review_required

@guard(model=Submission)
@block_if_task_exists('gcp_review')
def needs_gcp_review(wf):
    return wf.data.gcp_review_required

@guard(model=Submission)
@block_if_task_exists('paper_submission_review')
def needs_paper_submission_review(wf):
    return True
    
# b2 guards
@guard(model=Submission)
def is_b2(wf):
    return wf.data.newest_submission_form.current_pending_vote.result == '2'

@guard(model=Submission)
def is_still_b2(wf):
    vote = wf.data.newest_submission_form.current_pending_vote
    return vote.result == '2' and not vote.insurance_review_required and not vote.executive_review_required

@guard(model=Submission)
def needs_insurance_b2_review(wf):
    return wf.data.newest_submission_form.current_pending_vote.insurance_review_required

@guard(model=Submission)
def needs_executive_b2_review(wf):
    return wf.data.newest_submission_form.current_pending_vote.executive_review_required

##############
# Activities #
##############
class InitialReview(Activity):
    class Meta:
        model = Submission

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.initial_review', kwargs={'submission_pk': self.workflow.data_id})

    def get_choices(self):
        return (
            (True, _('Acknowledge')),
            (False, _('Reject')),
        )

    def pre_perform(self, choice):
        s = self.workflow.data
        sf = s.newest_submission_form
        sf.is_acknowledged = choice
        sf.save()
        on_initial_review.send(Submission, submission=s, form=sf)

class InitialThesisReview(InitialReview):
    def pre_perform(self, choice):
        super(InitialThesisReview, self).pre_perform(choice)
        s = self.workflow.data
        on_initial_thesis_review.send(Submission, submission=s, form=s.newest_submission_form)

class Resubmission(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.copy_latest_submission_form', kwargs={'submission_pk': self.workflow.data.pk})

    def get_final_urls(self):
        return super(Resubmission, self).get_final_urls() + [
            reverse('readonly_submission_form', kwargs={'submission_form_pk': sf})
            for sf in self.workflow.data.forms.values_list('pk', flat=True)
        ]

    def receive_token(self, *args, **kwargs):
        token = super(Resubmission, self).receive_token(*args, **kwargs)
        token.task.assign(self.workflow.data.presenter)
        return token


class B2ResubmissionReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.b2_vote_preparation', kwargs={'submission_form_pk': self.workflow.data.newest_submission_form.pk})


class InitialB2ResubmissionReview(B2ResubmissionReview):
    class Meta:
        model = Submission
        
    def get_choices(self):
        return (
            (None, _('Finish')),
            ('insrev', _('Insurance Review')),
            ('exerev', _('Executive Review')),
        )
        
    def pre_perform(self, choice):
        vote = self.workflow.data.newest_submission_form.current_pending_vote
        if choice == 'insrev':
            vote.executive_review_required = False
            vote.insurance_review_required = True
            vote.save()
        elif choice == 'exerev':
            vote.executive_review_required = True
            vote.insurance_review_required = False
            vote.save()
        else:
            vote.insurance_review_required = False
            vote.executive_review_required = False
            is_upgrade = vote.result != '2'
            if is_upgrade:
                vote.is_draft = False
            vote.save()
            if is_upgrade:
                on_b2_upgrade.send(Submission, submission=self.workflow.data, vote=vote)


class CategorizationReview(Activity):
    class Meta:
        model = Submission

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.categorization_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})

    def pre_perform(self, choice):
        s = self.workflow.data
        # create external review checklists
        blueprint = ChecklistBlueprint.objects.get(slug='external_review')
        for user in s.external_reviewers.all():
            checklist, created = Checklist.objects.get_or_create(blueprint=blueprint, submission=s, user=user)
            if created:
                for question in blueprint.questions.order_by('text'):
                    ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)

        with sudo():
            excats = list(s.expedited_review_categories.all())
            expedited_recommendation_tasks = Task.objects.for_data(s).filter(
                deleted_at__isnull=True, closed_at=None, task_type__workflow_node__uid='expedited_recommendation')
            expedited_recommendation_tasks.filter(assigned_to__isnull=False).exclude(expedited_review_categories__in=excats).mark_deleted()
            if not expedited_recommendation_tasks and s.workflow_lane == SUBMISSION_LANE_EXPEDITED:
                task_type = TaskType.objects.get(workflow_node__uid='expedited_recommendation', workflow_node__graph__auto_start=True)
                token = task_type.workflow_node.bind(self.workflow).receive_token(None)
                expedited_recommendation_tasks = [token.task]
            for task in expedited_recommendation_tasks:
                task.expedited_review_categories = excats

        on_categorization_review.send(Submission, submission=self.workflow.data)


class PaperSubmissionReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.paper_submission_review', kwargs={'submission_pk': self.workflow.data_id})


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
            return True
        return not checklist.is_complete

    def get_url(self):
        blueprint = self.node.data
        submission_form = self.workflow.data.current_submission_form
        return reverse('ecs.core.views.checklist_review', kwargs={'submission_form_pk': submission_form.pk, 'blueprint_pk': blueprint.pk})

    def pre_perform(self, choice):
        blueprint = self.node.data
        lookup_kwargs = {'blueprint': blueprint}
        if blueprint.multiple:
            lookup_kwargs['user'] = get_current_user()
        try:
            checklist = self.workflow.data.checklists.get(**lookup_kwargs)
        except Checklist.DoesNotExist:
            pass
        else:
            checklist.status = 'completed'
            checklist.save()

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
post_save.connect(unlock_non_repeatable_checklist_review, sender=Checklist)

class BoardMemberReview(ChecklistReview):
    def is_reentrant(self):
        return True

def unlock_boardmember_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(BoardMemberReview)
post_save.connect(unlock_boardmember_review, sender=Checklist)


class ExpeditedRecommendation(NonRepeatableChecklistReview):
    def is_reentrant(self):
        return True

    def receive_token(self, *args, **kwargs):
        token = super(ExpeditedRecommendation, self).receive_token(*args, **kwargs)
        s = self.workflow.data
        token.task.expedited_review_categories = s.expedited_review_categories.all()
        return token

def unlock_expedited_recommendation(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(ExpeditedRecommendation)
post_save.connect(unlock_expedited_recommendation, sender=Checklist)


class LocalEcRecommendation(ChecklistReview):
    def pre_perform(self, choice):
        super(LocalEcRecommendation, self).pre_perform(choice)
        if has_localec_recommendation(self.workflow):
            submission = self.workflow.data
            Vote.objects.create(result='1', text=get_checklist_comment(submission, 'localec_review', 1),
                submission_form=submission.current_submission_form, is_draft=True)

def unlock_localec_recommendation(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(LocalEcRecommendation)
post_save.connect(unlock_localec_recommendation, sender=Checklist)


class RecommendationReview(NonRepeatableChecklistReview):
    def is_reentrant(self):
        return True

def unlock_recommendation_review(sender, **kwargs):
    kwargs['instance'].submission.workflow.unlock(RecommendationReview)
post_save.connect(unlock_recommendation_review, sender=Checklist)


class VotePreparation(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.vote_preparation', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})


class WaitForMeeting(Generic):
    class Meta:
        model = Submission
        
    def is_locked(self):
        return not self.workflow.data.votes.exists()


@connect(meeting_signals.on_meeting_end)
def on_meeting_end(sender, **kwargs):
    meeting = kwargs['meeting']
    for submission in meeting.submissions.all():
        submission.workflow.unlock(WaitForMeeting)
    
