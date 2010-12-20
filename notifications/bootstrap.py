from ecs import bootstrap
from ecs.notifications.models import NotificationType, Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.utils import Args

@bootstrap.register()
def notification_types():
    types = (
        (u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", "ecs.core.forms.MultiNotificationForm", False, False),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm", False, True),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm", False, True),
        (u"Amendment", "ecs.core.forms.forms.AmendmentNotificationForm", True, True),
    )
    
    for name, form, diff, earfa in types:
        t, created = NotificationType.objects.get_or_create(name=name, form=form, diff=diff)
        if t.executive_answer_required_for_amg != earfa:
            t.executive_answer_required_for_amg = earfa
            t.save()


@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def notification_workflow():
    from ecs.notifications.workflow import EditNotificationAnswer, DistributeNotificationAnswer, SignNotificationAnswer, needs_executive_answer

    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    NOTIFICATION_REVIEW_GROUP = 'EC-Notification Review Group'

    setup_workflow_graph(Notification,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name="Start"),
            'notification_answer': Args(EditNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP),
            'executive_notification_answer': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP),
            'sign_notification_answer': Args(SignNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP),
            'sign_executive_notification_answer': Args(SignNotificationAnswer, group=EXECUTIVE_GROUP),
            'distribute_notification_answer': Args(DistributeNotificationAnswer, group=OFFICE_GROUP, end=True),
        },
        edges={
            ('start', 'notification_answer'): Args(guard=needs_executive_answer, negated=True),
            ('start', 'executive_notification_answer'): Args(guard=needs_executive_answer),
            ('notification_answer', 'sign_notification_answer'): None,
            ('executive_notification_answer', 'sign_executive_notification_answer'): None,
            ('sign_notification_answer', 'distribute_notification_answer'): None,
            ('sign_executive_notification_answer', 'distribute_notification_answer'): None,
        }
    )
