from django.utils.translation import ugettext_noop as _

from ecs import bootstrap
from ecs.notifications.models import NotificationType, Notification
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.utils import Args
from ecs.notifications.workflow import (
    InitialAmendmentReview, EditNotificationAnswer, AutoDistributeNotificationAnswer,
    SignNotificationAnswer, SimpleNotificationReview, WaitForMeeting,
    is_susar, is_report, is_center_close, is_amendment, is_rejected_and_final,
    is_substantial, needs_further_review, needs_signature, needs_distribution,
)


@bootstrap.register()
def notification_types():
    types = (
        dict(
            name = "Sicherheitsbericht (SUSAR / SAE / Jährlicher Sicherheitsbericht)", 
            form = "ecs.notifications.forms.SafetyNotificationForm",
            default_response = "Die Kommission nimmt diese Meldung ohne Einspruch zur Kenntnis.",
            includes_diff = False,
            grants_vote_extension = False,
            is_rejectable = False,
            finishes_study = False,
            position = 1,
        ),
        dict(
            name = "Verlängerung der Gültigkeit des Votums",
            form = "ecs.notifications.forms.ProgressReportNotificationForm",
            default_response = "",
            includes_diff = False,
            grants_vote_extension = True,
            is_rejectable = True,
            finishes_study = False,
            position = 2,
        ),
        dict(
            name = "Beendigung der Studie / Abschlussbericht",
            form = "ecs.notifications.forms.CompletionReportNotificationForm",
            default_response = "",
            includes_diff = False,
            grants_vote_extension = False,
            is_rejectable = True,
            finishes_study = True,
            position = 3,
        ),
        dict(
            name = "Amendment",
            form = "ecs.notifications.forms.AmendmentNotificationForm",
            default_response = "Die Kommission stimmt der vorgeschlagenen Protokolländerung zu.",
            includes_diff = True,
            grants_vote_extension = False,
            is_rejectable = True,
            finishes_study = False,
            position = 4,
        ),
        dict(
            name = "Zentrumsschließung",
            form = "ecs.notifications.forms.CenterCloseNotificationForm",
            default_response = "Die Kommission nimmt diese Meldung ohne Einspruch zur Kenntnis.",
            includes_diff = False,
            grants_vote_extension = False,
            is_rejectable = True,
            finishes_study = False,
            position = 5,
        ),
    )

    objs = set()
    for data in types:
        data = data.copy()
        t, created = NotificationType.objects.update_or_create(
            name=data.pop('name'), defaults=data)
        objs.add(t)
    NotificationType.objects.exclude(pk__in=[obj.pk for obj in objs]).delete()

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def notification_workflow():
    EXECUTIVE_GROUP = 'EC-Executive'
    OFFICE_GROUP = 'EC-Office'
    SIGNING_GROUP = 'EC-Signing'

    setup_workflow_graph(Notification,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name='Start'),
            'safety_review': Args(SimpleNotificationReview, group=OFFICE_GROUP, name=_('Safety Review')),
            'distribute_notification_answer': Args(AutoDistributeNotificationAnswer, name=_('Distribute Notification Answer')),

            # reports
            'office_report_review': Args(SimpleNotificationReview, group=OFFICE_GROUP, name=_('Office Notification Review')),
            'executive_report_review': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP, name=_('Executive Notification Review')),

            # amendments
            'initial_amendment_review': Args(InitialAmendmentReview, group=OFFICE_GROUP, name=_('Initial Amendment Review')),
            'executive_amendment_review': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP, name=_('Amendment Review')),
            'wait_for_meeting': Args(WaitForMeeting, name='Wait For Meeting'),
            'amendment_split': Args(Generic, name='Amendment Split'),
            'notification_answer_signing': Args(SignNotificationAnswer, group=SIGNING_GROUP, name=_('Amendment Answer Signing')),
        },
        edges=(
            (('start', 'safety_review'), Args(guard=is_susar)),
            (('start', 'office_report_review'), Args(guard=is_report)),
            (('start', 'office_report_review'), Args(guard=is_center_close)),
            (('start', 'initial_amendment_review'), Args(guard=is_amendment)),

            # safety reports
            (('safety_review', 'executive_report_review'), Args(guard=is_rejected_and_final, negated=True)),
            (('safety_review', 'distribute_notification_answer'), Args(guard=is_rejected_and_final)),

            # reports
            (('office_report_review', 'executive_report_review'), Args(guard=is_rejected_and_final, negated=True)),
            (('office_report_review', 'distribute_notification_answer'), Args(guard=is_rejected_and_final)),
            (('executive_report_review', 'start'), Args(guard=needs_further_review)),
            (('executive_report_review', 'distribute_notification_answer'), Args(guard=needs_further_review, negated=True)),

            # amendments
            (('initial_amendment_review', 'executive_amendment_review'), Args(guard=is_rejected_and_final, negated=True)),
            (('initial_amendment_review', 'distribute_notification_answer'), Args(guard=is_rejected_and_final)),
            (('executive_amendment_review', 'initial_amendment_review'), Args(guard=needs_further_review)),
            (('executive_amendment_review', 'amendment_split'), Args(guard=needs_further_review, negated=True)),
            (('amendment_split', 'wait_for_meeting'), Args(guard=is_substantial)),
            (('amendment_split', 'notification_answer_signing'), Args(guard=needs_signature)),
            (('amendment_split', 'distribute_notification_answer'), Args(guard=needs_distribution)),
            (('wait_for_meeting', 'initial_amendment_review'), Args(guard=needs_further_review)),
            (('wait_for_meeting', 'notification_answer_signing'), Args(guard=needs_further_review, negated=True)),
        )
    )
