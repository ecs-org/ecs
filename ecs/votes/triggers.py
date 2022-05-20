from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.template import loader

from ecs.votes import signals
from ecs.users.utils import sudo
from ecs.tasks.models import Task, TaskType
from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.checklists.models import Checklist
from ecs.communication.mailutils import deliver


@receiver(signals.on_vote_publication)
def on_vote_published(sender, **kwargs):
    vote = kwargs['vote']
    sf = vote.submission_form
    if sf and not sf.is_categorized_multicentric_and_local:
        parties = sf.get_presenting_parties()
        reply_receiver = None
        with sudo():
            try:
                task = Task.objects.for_data(vote).closed().filter(task_type__group__name='EC-Office').order_by('-closed_at')[0]
                reply_receiver = task.assigned_to
            except IndexError:
                pass
        parties.send_message(
            _('Vote {ec_number}').format(ec_number=vote.get_ec_number()),
            'submissions/vote_publish.txt',
            {'vote': vote},
            submission=sf.submission,
            reply_receiver=reply_receiver)
    receivers = set()
    if (sf.is_amg and not sf.is_categorized_multicentric_and_local) or (sf.is_mpg and not sf.is_categorized_multicentric_and_local):
        receivers |= set(settings.ECS_AMG_MPG_VOTE_RECEIVERS)
    if sf.is_categorized_multicentric_and_main:
        investigators = sf.investigators.filter(ethics_commission__vote_receiver__isnull=False)
        receivers |= set(investigators.values_list('ethics_commission__vote_receiver', flat=True))
    bits = (
        'AMG' if sf.is_amg else None,
        'MPG' if sf.is_mpg else None,
        sf.eudract_number if sf.is_amg else sf.submission.ec_number,
        'Votum {0}'.format(vote.result),
    )
    name = slugify('_'.join(str(bit) for bit in bits if bit is not None))
    vote_ct = ContentType.objects.get_for_model(Vote)
    doc = Document.objects.get(content_type=vote_ct, object_id=vote.id)
    vote_pdf = doc.retrieve_raw().read()
    attachments = ((name + '.pdf', vote_pdf, 'application/pdf'),)
    template = loader.get_template('meetings/email/basg.txt')
    text = str(template.render({}))
    for receiver in receivers:
        deliver(receiver, subject=name, message=text,
            from_email=settings.DEFAULT_FROM_EMAIL, attachments=attachments)

    if vote.is_recessed:
        meeting = sf.submission.schedule_to_meeting()
        meeting.update_assigned_categories()
        with sudo():
            tasks = Task.objects.for_submission(sf.submission).filter(task_type__workflow_node__uid='categorization', deleted_at=None)
            if tasks and not any(t for t in tasks if not t.closed_at):  # XXX
                tasks[0].reopen()
    elif vote.is_permanent:
        with sudo():
            Task.objects.for_data(sf.submission).exclude(
                task_type__workflow_node__uid='b2_review').open().mark_deleted()

            Task.objects.filter(
                content_type=ContentType.objects.get_for_model(Checklist),
                data_id__in=sf.submission.checklists.values('id')
            ).open().mark_deleted()
    elif vote.result == '2':
        with sudo():
            Task.objects.for_submission(sf.submission).filter(
                task_type__is_dynamic=True).open().mark_deleted()

        task_type = TaskType.objects.get(workflow_node__uid='b2_resubmission', workflow_node__graph__auto_start=True)
        task_type.workflow_node.bind(sf.submission.workflow.workflows[0]).receive_token(None)
