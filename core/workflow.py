import datetime
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from ecs.workflow import Activity, guard, register
from ecs.core.models import Submission, ChecklistBlueprint, Vote

register(Submission, autostart_if=lambda s: bool(s.current_submission_form_id))
register(Vote)

@guard(model=Submission)
def is_acknowledged(wf):
    return wf.data.current_submission_form.acknowledged
    

@guard(model=Submission)
def is_thesis(wf):
    if wf.data.thesis is None:
        return wf.data.current_submission_form.project_type_education_context is not None
    return wf.data.thesis
    

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
    return wf.data.final
    
@guard(model=Vote)
def is_b2upgrade(wf):
    return False # FIXME

@guard(model=Submission)
def is_expedited(wf):
    return bool(wf.data.expedited)
    

@guard(model=Submission)
def has_recommendation(wf):
    return False # FIXME


@guard(model=Submission)
def has_accepted_recommendation(wf):
    return False # FIXME

@guard(model=Submission)
def needs_external_review(wf):
    return wf.data.external_reviewer
    
class InitialReview(Activity):
    class Meta:
        model = Submission
    
    def get_url(self):
        return reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': self.workflow.data.pk})
        
    def get_choices(self):
        return (
            (True, _('Acknowledge')),
            (False, _('Reject')),
        )
        
    def pre_perform(self, choice):
        sf = self.workflow.data.current_submission_form
        sf.acknowledged = choice
        sf.save()


class Resubmission(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return reverse('ecs.core.views.copy_latest_submission_form', kwargs={'submission_pk': self.workflow.data.pk})

class B2VoteReview(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return reverse('ecs.core.views.b2_vote_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form.pk})

class CategorizationReview(Activity):
    class Meta:
        model = Submission
        
    def is_repeatable(self):
        return True
        
    def get_url(self):
        return reverse('ecs.core.views.categorization_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form.pk})


class PaperSubmissionReview(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return None # FIXME


class ChecklistReview(Activity):
    class Meta:
        model = Submission
        vary_on = ChecklistBlueprint
        
    def is_reentrant(self):
        return False
        
    def get_url(self):
        blueprint = self.node.data
        submission_form = self.workflow.data.current_submission_form
        return reverse('ecs.core.views.checklist_review', kwargs={'submission_form_pk': submission_form.pk, 'blueprint_pk': blueprint.pk})


class VoteRecommendation(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return None # FIXME


class VoteRecommendationReview(Activity):
    class Meta:
        model = Submission
        
    def get_url(self):
        return None # FIXME


class ExternalReview(Activity):
    class Meta:
        model = Submission

    def get_url(self):
        return None # FIXME
        
class ExternalReviewInvitation(Activity):
    class Meta:
        model = Submission


class VoteFinalization(Activity):
    class Meta:
        model = Vote
    
    def get_url(self):
        return reverse('ecs.core.views.vote_review', kwargs={'submission_form_pk': self.workflow.data.current_submission_form_id})


class VoteReview(Activity):
    class Meta:
        model = Vote
        
    def get_url(self):
        return None # FIXME


class VoteSigning(Activity):
    class Meta:
        model = Vote
        
    def get_url(self):
        return None # FIXME


class VotePublication(Activity):
    class Meta:
        model = Vote

    def get_url(self):
        return None # FIXME
