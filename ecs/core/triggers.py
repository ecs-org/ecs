from django.dispatch import receiver
from django.utils.translation import ugettext as _

from ecs.communication.utils import send_system_message_template
from ecs.core import signals
from ecs.tasks.models import Task
from ecs.users.utils import sudo, get_current_user
from ecs.users.utils import get_office_user
from ecs.votes.constants import PERMANENT_VOTE_RESULTS
from ecs.core.models.constants import SUBMISSION_LANE_RETROSPECTIVE_THESIS, \
    SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_BOARD, SUBMISSION_LANE_LOCALEC


def send_submission_message(submission, user, subject, template, **kwargs):
    send_system_message_template(user, subject.format(ec_number=submission.get_ec_number_display()), template, None, submission=submission, **kwargs)


@receiver(signals.on_study_change)
def on_study_change(sender, **kwargs):
    submission = kwargs['submission']
    old_sf, new_sf = kwargs['old_form'], kwargs['new_form']
    
    if not old_sf: # first version of the submission
        for u in new_sf.get_involved_parties().get_users().difference([submission.presenter]):
            send_submission_message(submission, u, _('Submission of study EC-Nr. {ec_number}'), 'submissions/creation_message.txt', reply_receiver=submission.presenter)
    else:
        reopen = True

        current_vote = submission.current_published_vote
        if current_vote:
            if current_vote.result in PERMANENT_VOTE_RESULTS:
                reopen = False
            elif current_vote.result == '2':
                pending_vote = submission.current_pending_vote
                if not pending_vote or pending_vote.is_draft:
                    reopen = False

        if reopen:
            with sudo():
                initial_review_tasks = Task.objects.for_data(submission).filter(
                    task_type__workflow_node__uid__in=(
                        'initial_review', 'initial_thesis_review'),
                    deleted_at=None,
                )

                if not initial_review_tasks.open().exists():
                    initial_review_tasks.order_by('-created_at').first().reopen()


@receiver(signals.on_study_submit)
def on_study_submit(sender, **kwargs):
    submission = kwargs['submission']
    submission_form = kwargs['form']
    user = kwargs['user']

    submission_form.render_pdf_document()

    resubmission_task = Task.objects.for_user(user).for_data(submission).filter(
        task_type__workflow_node__uid__in=('resubmission', 'b2_resubmission')
    ).open().first()
    if resubmission_task:
        resubmission_task.done(user)


@receiver(signals.on_presenter_change)
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


@receiver(signals.on_susar_presenter_change)
def on_susar_presenter_change(sender, **kwargs):
    submission = kwargs['submission']
    user = kwargs['user']
    old_susar_presenter, new_susar_presenter = kwargs['old_susar_presenter'], kwargs['new_susar_presenter']

    send_submission_message(submission, new_susar_presenter, _('Studie {ec_number}'), 'submissions/susar_presenter_change_new.txt')
    if user != old_susar_presenter:
        send_submission_message(submission, old_susar_presenter, _('Studie {ec_number}'), 'submissions/susar_presenter_change_previous.txt')


@receiver(signals.on_initial_review)
def on_initial_review(sender, **kwargs):
    submission, submission_form = kwargs['submission'], kwargs['form']

    if submission_form.is_acknowledged:
        send_submission_message(submission, submission.presenter, _('Acknowledgement of Receipt'), 'submissions/acknowledge_message.txt')
        if not submission.current_submission_form == submission_form:
            pending_vote = submission.current_pending_vote
            if pending_vote and pending_vote.is_draft:
                pending_vote.submission_form = submission_form
                pending_vote.save()
            submission_form.mark_current()
            vote = submission.current_published_vote
            if vote and vote.is_recessed:
                receivers = submission_form.get_presenting_parties().get_users()
                with sudo():
                    for task in Task.objects.for_submission(submission).filter(task_type__workflow_node__uid__in=['categorization', 'internal_vote_review'], assigned_to__isnull=False):
                        receivers.add(task.assigned_to)
                    for task in Task.objects.for_submission(submission).filter(task_type__workflow_node__uid='specialist_review', assigned_to__isnull=False).open():
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
    ),
    SUBMISSION_LANE_EXPEDITED : (
        'expedited_recommendation',
    ),
    SUBMISSION_LANE_BOARD : (
        'specialist_review',
    ),
    SUBMISSION_LANE_LOCALEC : (
        'localec_recommendation',
    ),
}

VOTE_PREPARATION_SOURCES = {
    SUBMISSION_LANE_RETROSPECTIVE_THESIS: 'thesis_recommendation_review',
    SUBMISSION_LANE_EXPEDITED: 'expedited_recommendation',
    SUBMISSION_LANE_LOCALEC: 'localec_recommendation',
}


@receiver(signals.on_categorization)
def on_categorization(sender, **kwargs):
    submission = kwargs['submission']

    meeting = submission.schedule_to_meeting()
    meeting.update_assigned_categories()

    with sudo():
        tasks = Task.objects.for_submission(submission).open()
        for lane, uids in LANE_TASKS.items():
            if not submission.workflow_lane == lane:
                tasks.filter(task_type__workflow_node__uid__in=uids).mark_deleted()

        if submission.workflow_lane == SUBMISSION_LANE_RETROSPECTIVE_THESIS:
            for task in tasks.filter(task_type__workflow_node__uid='initial_review'):
                if task.workflow_node.graph.nodes.filter(uid='initial_thesis_review').exists():
                    task.mark_deleted()

        vote_preparation_tasks = tasks.filter(
            task_type__workflow_node__uid='vote_preparation')
        source_uid = VOTE_PREPARATION_SOURCES.get(submission.workflow_lane)
        for task in vote_preparation_tasks:
            if task.workflow_token.source.uid != source_uid:
                task.mark_deleted()
