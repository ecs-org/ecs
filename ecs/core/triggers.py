from django.utils.translation import ugettext as _

from ecs.communication.utils import send_system_message_template
from ecs.core.workflow import InitialReview
from ecs.core import signals
from ecs.tasks.models import Task
from ecs.tasks.utils import get_obj_tasks
from ecs.users.utils import sudo, get_current_user
from ecs.utils import connect
from ecs.users.utils import get_office_user
from ecs.votes.constants import FINAL_VOTE_RESULTS
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS, \
    SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_BOARD, SUBMISSION_LANE_LOCALEC
from ecs.votes.signals import on_vote_expiry, on_vote_extension


def send_submission_message(submission, user, subject, template, **kwargs):
    send_system_message_template(user, subject.format(ec_number=submission.get_ec_number_display()), template, None, submission=submission, **kwargs)


@connect(signals.on_study_change)
def on_study_change(sender, **kwargs):
    submission = kwargs['submission']
    old_sf, new_sf = kwargs['old_form'], kwargs['new_form']
    
    if not old_sf: # first version of the submission
        for u in new_sf.get_involved_parties().get_users().difference([submission.presenter]):
            send_submission_message(submission, u, _('Submission of study EC-Nr. {ec_number}'), 'submissions/creation_message.txt', reply_receiver=submission.presenter)
    else:
        with sudo():
            if not submission.votes.filter(is_draft=False, result__in=FINAL_VOTE_RESULTS).exists():
                initial_review_tasks = get_obj_tasks((InitialReview,), submission)
                try:
                    initial_review_task = initial_review_tasks.exclude(closed_at__isnull=True).order_by('-created_at')[0]
                except IndexError:
                    pass
                else:
                    if not initial_review_tasks.open().exists():
                        initial_review_task.reopen()


@connect(signals.on_study_submit)
def on_study_submit(sender, **kwargs):
    submission = kwargs['submission']
    submission_form = kwargs['form']
    user = kwargs['user']

    submission_form.render_pdf()
    
    resubmission_task = submission.resubmission_task_for(user)
    if resubmission_task:
        resubmission_task.done(user)

    b2_resubmission_task = submission.b2_resubmission_task_for(user)
    if b2_resubmission_task:
        b2_resubmission_task.done(user)


@connect(signals.on_presenter_change)
def on_presenter_change(sender, **kwargs):
    submission = kwargs['submission']
    user = kwargs['user']
    old_presenter, new_presenter = kwargs['old_presenter'], kwargs['new_presenter']
    
    send_submission_message(submission, new_presenter, _('Studie {ec_number}'), 'submissions/presenter_change_new.txt')
    if user != old_presenter:
        send_submission_message(submission, old_presenter, _('Studie {ec_number}'), 'submissions/presenter_change_previous.txt')

    with sudo():
        for task in Task.objects.for_data(submission).filter(task_type__workflow_node__uid__in=['resubmission', 'b2_resubmission']).open():
            task.assign(new_presenter)


@connect(signals.on_susar_presenter_change)
def on_susar_presenter_change(sender, **kwargs):
    submission = kwargs['submission']
    user = kwargs['user']
    old_susar_presenter, new_susar_presenter = kwargs['old_susar_presenter'], kwargs['new_susar_presenter']

    send_submission_message(submission, new_susar_presenter, _('Studie {ec_number}'), 'submissions/susar_presenter_change_new.txt')
    if user != old_susar_presenter:
        send_submission_message(submission, old_susar_presenter, _('Studie {ec_number}'), 'submissions/susar_presenter_change_previous.txt')


@connect(signals.on_initial_review)
def on_initial_review(sender, **kwargs):
    submission, submission_form = kwargs['submission'], kwargs['form']

    if submission_form.is_acknowledged:
        if submission.workflow_lane == SUBMISSION_LANE_RETROSPECTIVE_THESIS:
            with sudo():
                meeting = submission.schedule_to_meeting()
                meeting.update_assigned_categories()

        send_submission_message(submission, submission.presenter, _('Acknowledgement of Receipt'), 'submissions/acknowledge_message.txt')
        if not submission.current_submission_form == submission_form:
            current_vote = submission.current_submission_form.current_vote
            if current_vote and current_vote.is_draft:
                current_vote.submission_form = submission_form
                current_vote.save()
            submission_form.mark_current()
            vote = submission.get_most_recent_vote(is_draft=False, published_at__isnull=False)
            if vote and vote.is_recessed:
                receivers = submission_form.get_presenting_parties().get_users()
                with sudo():
                    for task in Task.objects.for_submission(submission).filter(task_type__workflow_node__uid__in=['categorization_review', 'internal_vote_review'], assigned_to__isnull=False):
                        receivers.add(task.assigned_to)
                    for task in Task.objects.for_submission(submission).filter(task_type__workflow_node__uid='board_member_review', assigned_to__isnull=False).open():
                        receivers.add(task.assigned_to)
            else:
                receivers = submission_form.get_involved_parties().get_users()
            receivers = receivers.difference([submission_form.presenter, get_current_user()])
            for u in receivers:
                send_submission_message(submission, u, _('Changes to study EC-Nr. {ec_number}'), 'submissions/change_message.txt', reply_receiver=get_office_user(submission=submission))
    else:
        send_submission_message(submission, submission.presenter, _('Submission not accepted'), 'submissions/decline_message.txt')


LANE_TASKS = {
    SUBMISSION_LANE_RETROSPECTIVE_THESIS : (
        'initial_thesis_review',
        'thesis_recommendation',
        'thesis_recommendation_review',
        'thesis_vote_preparation',
    ),
    SUBMISSION_LANE_EXPEDITED : (
        'expedited_recommendation',
        'expedited_vote_preparation',
    ),
    SUBMISSION_LANE_BOARD : (
        'board_member_review',
    ),
    SUBMISSION_LANE_LOCALEC : (
        'localec_recommendation',
        'localec_vote_preparation',
    ),
}


@connect(signals.on_categorization_review)
def on_categorization_review(sender, **kwargs):
    submission = kwargs['submission']

    meeting = submission.schedule_to_meeting()
    meeting.update_assigned_categories()

    with sudo():
        tasks = Task.objects.for_submission(submission).open()
        for lane, uids in LANE_TASKS.items():
            if not submission.workflow_lane == lane:
                tasks.filter(task_type__workflow_node__uid__in=uids).mark_deleted()
        if submission.workflow_lane == SUBMISSION_LANE_RETROSPECTIVE_THESIS:
            tasks.filter(task_type__workflow_node__uid='initial_review').mark_deleted()


@connect(signals.on_b2_upgrade)
def on_b2_upgrade(sender, **kwargs):
    submission, vote = kwargs['submission'], kwargs['vote']
    vote.submission_form.is_acknowledged = True
    vote.submission_form.save()
    vote.submission_form.mark_current()


@connect(on_vote_expiry)
def expire_submission(sender, **kwargs):
    vote = kwargs['vote']
    submission = vote.get_submission()
    if submission and not submission.is_localec and vote.is_positive and vote.is_permanent:
        submission.expire()


@connect(on_vote_extension)
def extend_submission(sender, **kwargs):
    vote = kwargs['vote']
    submission = vote.get_submission()
    if submission:
        submission.is_expired = False
        submission.save()
