from django.utils.translation import ugettext as _

from ecs.communication.utils import send_system_message_template
from ecs.core.workflow import InitialReview
from ecs.tasks.utils import get_obj_tasks
from ecs.users.utils import sudo
from ecs.core import signals
from ecs.utils import connect
from ecs.checklists.utils import get_checklist_answer


def send_submission_message(submission, user, subject, template):
    send_system_message_template(user, _(subject).format(ec_number=submission.get_ec_number_display()), template, None, submission=submission)


@connect(signals.on_study_change)
def on_study_change(sender, **kwargs):
    submission = kwargs['submission']
    old_sf, new_sf = kwargs['old_form'], kwargs['new_form']
    
    involved_users = set([p.user for p in new_sf.get_involved_parties() if p.user and not p.user == new_sf.presenter])
    if not old_sf: # first version of the submission
        for u in involved_users:
            send_submission_message(submission, u, 'Creation of study EC-Nr. {ec_number}', 'submissions/creation_message.txt')
    else:
        with sudo():
            try:
                initial_review_task = get_obj_tasks((InitialReview,), submission).exclude(closed_at__isnull=True)[0]
            except IndexError:
                pass
            else:
                initial_review_task.reopen()
                send_submission_message(submission, initial_review_task.assigned_to, 'Creation of study EC-Nr. {ec_number}', 'submissions/creation_message.txt')


@connect(signals.on_study_submit)
def on_study_submit(sender, **kwargs):
    submission = kwargs['submission']
    submission_form = kwargs['form']
    user = kwargs['user']

    submission_form.render_pdf()
    
    resubmission_task = submission.resubmission_task_for(user)
    if resubmission_task:
        resubmission_task.done(user)


@connect(signals.on_presenter_change)
def on_presenter_change(sender, **kwargs):
    submissiom, submission_form = kwargs['submission'], kwargs['form']
    user = kwargs['user']
    old_presenter, new_presenter = kwargs['old_presenter'], kwargs['new_presenter']
    
    send_submission_message(submission, new_presenter, 'Studie {ec_number}', 'submissions/presenter_change_new.txt')
    if user != old_presenter:
        send_submission_message(submission, old_presenter, 'Studie {ec_number}', 'submissions/presenter_change_previous.txt')


@connect(signals.on_susar_presenter_change)
def on_susar_presenter_change(sender, **kwargs):
    submissiom, submission_form = kwargs['submission'], kwargs['form']
    user = kwargs['user']
    old_susar_presenter, new_susar_presenter = kwargs['old_presenter'], kwargs['new_presenter']

    send_submission_message(submission, new_susar_presenter, 'Studie {ec_number}', 'submissions/susar_presenter_change_new.txt')
    if user != old_susar_presenter:
        send_submission_message(submission, old_susar_presenter, 'Studie {ec_number}', 'submissions/susar_presenter_change_previous.txt')


@connect(signals.on_initial_review)
def on_initial_review(sender, **kwargs):
    submission, submission_form = kwargs['submission'], kwargs['form']
    if submission_form.is_acknowledged:
        send_submission_message(submission, submission_form.presenter, 'Submission accepted', 'submissions/acknowledge_message.txt')
        if not submission.current_submission_form == submission_form:
            submission_form.mark_current()
            involved_users = set([p.user for p in submission_form.get_involved_parties() if p.user and not p.user == submission_form.presenter])
            for u in involved_users:
                send_submission_message(submission, u, 'Changes to study EC-Nr. {ec_number}', 'submissions/change_message.txt')
    else:
        send_submission_message(submission, 'Submission not accepted', 'submissions/decline_message.txt')


@connect(signals.on_categorization_review)
def on_categorization_review(sender, **kwargs):
    submission = kwargs['submission']
    
    # FIXME: this could use some cleanup
    is_retrospective_thesis = Submission.objects.retrospective_thesis().filter(pk=submission.pk).exists()
    is_special = submission.is_expedited or is_retrospective_thesis or submission.current_submission_form.is_categorized_multicentric_and_local
    is_acknowledged = submission.newest_submission_form.is_acknowledged
    
    if is_acknowledged and (not is_special or submission.meetings.filter(started=None).exists()):
        submission.schedule_to_meeting()


@connect(signals.on_thesis_recommendation_review)
def on_thesis_recommendation_review(sender, **kwargs):
    submission = kwargs['submission']
    if get_checklist_answer(submission, 'thesis_review', 1):
        submission.schedule_to_meeting()


@connect(signals.on_expedited_recommendation_review)
def on_expedited_recommendation_review(sender, **kwargs):
    submission = kwargs['submission']
    if get_checklist_answer(submission, 'expedited_review', 1):
        submission.schedule_to_meeting()


@connect(signals.on_local_ec_recommendation_review)
def on_local_ec_recommendation_review(sender, **kwargs):
    submission = kwargs['submission']
    submission.schedule_to_meeting()
    
    
