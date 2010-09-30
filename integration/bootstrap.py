from ecs.utils import args
from ecs.workflow.patterns import Generic
from ecs.workflow.utils import setup_workflow

def submission_workflow():
    from ecs.core.models import Submission
    from ecs.core.workflow import (InitialReview, Resubmission, CategorizationReview, PaperSubmissionReview, 
        ChecklistReview, BoardMemberReview, ExternalReview, VoteRecommendation, VoteRecommendationReview)
    from ecs.core.workflow import is_accepted, is_thesis, is_expedited, has_recommendation, has_accepted_recommendation
    
    setup_workflow(Submission,
        autostart=True,
        nodes={
            'start': Args(Generic),
            'generic_review': Args(Generic),
            'resubmission': Args(Resubmission),
            'initial_review': Args(InitialReview),
            'categorization_review' Args(CategorizationReview),
            'initial_thesis_review' Args(InitialReview),
            'thesis_categorization_review' Args(CategorizationReview),
            'paper_submission_review': Args(PaperSubmissionReview),
            'legal_and_patient_review': Args(ChecklistReview, data={'name': 'LegalAndPatientReview'}, name=u"Legal and Patient Review"),
            'insurance_review': Args(ChecklistReview, data={'name': 'InsuranceReview'}, name=u"Insurance Review"),
            'statistical_review': Args(ChecklistReview, data={'name': 'StatisticalReview'}, name=u"Statistical Review"),
            'board_member_review': Args(BoardMemberReview, data={'name': 'BoardMemberReview'}, name=u"Board Member Review"),
            'external_review': Args(ExternalReview),
            'thesis_vote_recommendation': Args(VoteRecommendation),
            'vote_recommendation_review': Args(VoteRecommendationReview),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_thesis, negated=True),
            ('start', 'initial_thesis_review'): Args(guard=is_thesis),

            ('initial_review', 'resubmission'): Args(guard=is_accepted, negated=True),
            ('initial_review', 'categorization_review'): Args(guard=is_accepted),
            ('initial_review', 'paper_submission_review'): None,

            ('initial_thesis_review', 'resubmission'): Args(guard=is_accepted, negated=True),
            ('initial_thesis_review', 'thesis_categorization_review'): Args(guard=is_accepted),
            ('initial_thesis_review', 'paper_submission_review'): None,

            ('thesis_categorization_review', 'thesis_vote_recommendation'): None,

            ('thesis_vote_recommendation', 'vote_recommendation_review'): Args(guard=has_recommendation),
            ('thesis_vote_recommendation', 'categorization_review'): Args(guard=has_recommendation, negated=True),

            ('vote_recommendation_review', None): Args(guard=has_accepted_recommendation),
            ('vote_recommendation_review', 'categorization_review'): Args(guard=has_accepted_recommendation, negated=True),

            ('categorization_review', None): Args(guard=is_expedited),
            ('categorization_review', 'generic_review'): Args(guard=is_expedited, negated=True),

            ('generic_review', 'board_member_review'): None,
            ('generic_review', 'insurance_review'): None,
            ('generic_review', 'statistical_review'): None,
            ('generic_review', 'legal_and_patient_review'): None,
        }
    )


def vote_workflow():
    from ecs.core.models import Vote
    from ecs.core.workflow import VoteFinalization, VoteReview, VoteSigning, VotePublication

    setup_workflow(Vote, 
        autostart=True, 
        nodes={
            'vote_finalization': Args(VoteFinalization),
            'vote_review': Args(VoteFinalization),
            'office_vote_finalization': Args(VoteFinalization),
            'office_vote_review': Args(VoteReview),
            'vote_signing': Args(VoteSigning),
            'vote_publication': Args(VotePublication),
        }, 
        edges={
        
        }
    )


def meeting_workflow():
    from ecs.meetings.models import Meeting
    from ecs.meetings.workflow import MeetingAgendaPreparation, MeetingAgendaSending, MeetingDay, MeetingProtocolSending

    setup_workflow(Meeting, 
        autostart=True, 
        nodes={
            'meeting_agenda_generation': Args(MeetingAgendaPreparation, start=True),
            'meeting_agenda_sending': Args(MeetingAgendaSending),
            'meeting_day': Args(MeetingDay),
            'meeting_protocol_sending': Args(MeetingProtocolSending, end=True),
        }, 
        edges={
            ('meeting_agenda_generation', 'meeting_agenda_sending'): None,
            ('meeting_agenda_sending', 'meeting_day'): None,
            ('meeting_day', 'meeting_protocol_sending'): None,
        }
    )


