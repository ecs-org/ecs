from django.contrib.contenttypes.models import ContentType
from ecs import authorization
from ecs.core.models import Submission, SubmissionForm, Investigator, InvestigatorEmployee, Measure, ForeignParticipatingCenter, NonTestedUsedDrug, Vote
from ecs.documents.models import Document
from ecs.core.models.voting import FINAL_VOTE_RESULTS
from ecs.docstash.models import DocStash

class SubmissionQFactory(authorization.QFactory):
    def get_q(self, user):
        profile = user.get_profile()

        ### shortcircuit logic
        if not profile.approved_by_office:
            return self.make_deny_q()

        ### default policy: deny access to all submissions.
        q = self.make_deny_q()

        ### rules that apply until a final vote has been published.
        until_vote_q = self.make_q(additional_reviewers=user)
        if profile.thesis_review:
            until_vote_q |= self.make_q(thesis=True)
        if profile.board_member:
            until_vote_q |= self.make_q(timetable_entries__participations__user=user, timetable_entries__meeting=self.make_f('next_meeting'))
        if profile.expedited_review:
            until_vote_q |= self.make_q(expedited=True)
        if profile.external_review:
            until_vote_q |= self.make_q(external_reviewer_name=user)
        # FIXME: how do we detect whether an insurance review is required?
        #if profile.insurance_review:
        #    until_vote_q |= self.make_q(insurance_review_required=True)
        q |= until_vote_q & (
            self.make_q(current_submission_form__current_published_vote=None)
            | ~self.make_q(current_submission_form__current_published_vote__result__in=FINAL_VOTE_RESULTS)
        )

        ### rules that apply until the end of the submission lifecycle
        until_eol_q = self.make_q(pk__gt=0) # active=True
        if not (user.is_staff or profile.internal):
            until_eol_q &= self.make_q(current_submission_form__submitter=user) | self.make_q(current_submission_form__primary_investigator__user=user) | self.make_q(current_submission_form__sponsor=user)
        q |= until_eol_q
        return q

authorization.register(Submission, factory=SubmissionQFactory)
authorization.register(SubmissionForm, lookup='submission')
authorization.register(Investigator, lookup='submission_form__submission')
authorization.register(InvestigatorEmployee, lookup='investigator__submission_form__submission')
authorization.register(Measure, lookup='submission_form__submission')
authorization.register(NonTestedUsedDrug, lookup='submission_form__submission')
authorization.register(ForeignParticipatingCenter, lookup='submission_form__submission')
authorization.register(Vote, lookup='submission_form__submission')

class DocumentQFactory(authorization.QFactory):
    def get_q(self, user):
        submission_q = self.make_q(content_type=ContentType.objects.get_for_model(SubmissionForm))
        q = ~submission_q | (submission_q & self.make_q(object_id__in=SubmissionForm.objects.values('pk').query))
        return q

authorization.register(Document, factory=DocumentQFactory)

class DocstashQFactory(authorization.QFactory):
    def get_q(self, user):
        return self.make_q(owner=user)

authorization.register(DocStash, factory=DocstashQFactory)
