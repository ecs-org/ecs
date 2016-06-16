from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from ecs.workflow import Activity, guard, register
from ecs.workflow.patterns import Generic
from ecs.users.utils import get_current_user, sudo
from ecs.core.models import Submission
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS
from ecs.core.signals import on_initial_review, on_categorization_review, on_b2_upgrade
from ecs.checklists.models import ChecklistBlueprint, Checklist, ChecklistAnswer
from ecs.checklists.utils import get_checklist_answer
from ecs.tasks.models import Task
from ecs.tasks.utils import block_duplicate_task, block_if_task_exists
from ecs.votes.models import Vote

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
    return wf.data.is_expedited

@guard(model=Submission)
def is_expedited_or_retrospective_thesis(wf):
    return is_expedited(wf) or is_retrospective_thesis(wf)

#########################
# recommendation guards #
#########################
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

@guard(model=Submission)
@block_duplicate_task('vote_preparation')
@block_duplicate_task('expedited_vote_preparation')     # XXX: compat
def needs_expedited_vote_preparation(wf):
    with sudo():
        unfinished = wf.tokens.filter(node__graph__workflows=wf, node__uid='expedited_recommendation', consumed_at__isnull=True).exists()
        negative = ChecklistAnswer.objects.filter(question__number='1', answer=False, checklist__submission=wf.data, checklist__blueprint__slug='expedited_review')
        return not unfinished and not negative.exists()

@guard(model=Submission)
@block_duplicate_task('categorization_review')
def needs_expedited_recategorization(wf):
    with sudo():
        unfinished = wf.tokens.filter(node__graph__workflows=wf, node__uid='expedited_recommendation', consumed_at__isnull=True).exists()
        negative = ChecklistAnswer.objects.filter(question__number='1', answer=False, checklist__submission=wf.data, checklist__blueprint__slug='expedited_review')
        return not unfinished and negative.exists()

@guard(model=Submission)
def has_expedited_recommendation(wf):
    ''' legacy: to be removed '''
    return not needs_expedited_recategorization(wf)

@guard(model=Submission)
@block_duplicate_task('localec_recommendation')
def needs_localec_recommendation(wf):
    return wf.data.is_localec

@guard(model=Submission)
@block_duplicate_task('vote_preparation')
@block_duplicate_task('localec_vote_preparation')       # XXX: compat
def needs_localec_vote_preparation(wf):
    return has_localec_recommendation(wf)

# b2 guards
@guard(model=Submission)
@block_duplicate_task('b2_resubmission')
def is_b2(wf):
    return wf.data.get_most_recent_vote().result == '2'

@guard(model=Submission)
def is_still_b2(wf):
    vote = wf.data.get_most_recent_vote()
    return vote.result == '2' and not vote.insurance_review_required and not vote.executive_review_required

@guard(model=Submission)
def needs_insurance_b2_review(wf):
    vote = wf.data.get_most_recent_vote()
    return vote.insurance_review_required

@guard(model=Submission)
def needs_executive_b2_review(wf):
    vote = wf.data.get_most_recent_vote()
    return vote.executive_review_required


##############
# Activities #
##############

class InitialReview(Activity):
    class Meta:
        model = Submission

    def is_repeatable(self):
        return True

    def get_url(self):
        return reverse('ecs.core.views.submissions.initial_review', kwargs={'submission_pk': self.workflow.data_id})

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


class Resubmission(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.submissions.copy_latest_submission_form', kwargs={'submission_pk': self.workflow.data_id})

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
        return reverse('ecs.core.views.submissions.b2_vote_preparation', kwargs={'submission_form_pk': self.workflow.data.newest_submission_form.pk})


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
        vote = self.workflow.data.get_most_recent_vote()
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
        return reverse('ecs.core.views.submissions.categorization_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})

    def is_locked(self):
        with sudo():
            s = self.workflow.data
        return not s.allows_categorization()

    def pre_perform(self, choice):
        s = self.workflow.data
        on_categorization_review.send(Submission, submission=s)
        blueprint = ChecklistBlueprint.objects.get(slug='external_review')
        for user in s.external_reviewers.all():
            checklist, created = Checklist.objects.get_or_create(blueprint=blueprint, submission=s, user=user, defaults={'last_edited_by': user})
            if created:
                for question in blueprint.questions.order_by('text'):
                    checklist.answers.get_or_create(question=question)
            elif checklist.status == 'dropped':
                checklist.status = 'new'
                checklist.save()
                with sudo():
                    tasks = Task.objects.for_data(checklist).filter(task_type__workflow_node__uid='external_review')
                    if not any(t for t in tasks if not t.closed_at and not t.deleted_at):
                        tasks[0].reopen()
        for checklist in Checklist.objects.filter(blueprint=blueprint, submission=s).exclude(user__in=s.external_reviewers.values('pk').query):
            checklist.status = 'dropped'
            checklist.save()
            with sudo():
                Task.objects.for_data(checklist).open().mark_deleted()

def unlock_categorization_review(sender, **kwargs):
    kwargs['instance'].workflow.unlock(CategorizationReview)
post_save.connect(unlock_categorization_review, sender=Submission)

class ExpeditedRecommendationSplit(Generic):
    class Meta:
        model = Submission

    def emit_token(self, *args, **kwargs):
        s = self.workflow.data
        with sudo():
            tasks = Task.objects.for_data(s).filter(
                deleted_at__isnull=True, task_type__workflow_node__uid='expedited_recommendation')
            tasks.filter(assigned_to__isnull=True, closed_at=None).exclude(
                medical_category__in=s.medical_categories.values('pk')).mark_deleted()
            missing_cats = list(s.medical_categories.exclude(
                pk__in=tasks.values('medical_category_id')))

        tokens = []
        for cat in missing_cats:
            cat_tokens = super(ExpeditedRecommendationSplit, self).emit_token(*args, **kwargs)
            for token in cat_tokens:
                token.task.medical_category = cat
                token.task.save()
            tokens += cat_tokens
        return tokens


class PaperSubmissionReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return reverse('ecs.core.views.submissions.paper_submission_review', kwargs={'submission_pk': self.workflow.data_id})


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
        blueprint_id = self.node.data_id
        submission_form_id = self.workflow.data.current_submission_form_id
        return reverse('ecs.core.views.submissions.checklist_review', kwargs={'submission_form_pk': submission_form_id, 'blueprint_pk': blueprint_id})

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
        return reverse('ecs.core.views.submissions.vote_preparation', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})


### to be deleted
class WaitForMeeting(Generic):
    class Meta:
        model = Submission

    def is_locked(self):
        return True
