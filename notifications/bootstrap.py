# -*- coding: utf-8 -*-
from ecs import bootstrap
from ecs.notifications.models import NotificationType, Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.utils import Args
from ecs.bootstrap.utils import update_instance


# for marking the task names translatable
_ = lambda s: s

@bootstrap.register()
def notification_types():
    types = (
        (u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", "ecs.core.forms.SusarNotificationForm", False, False, u"Die Kommission nimmt diese Meldung ohne Einspruch zur Kenntnis."),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm", False, True, u""),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm", False, False, u""),
        (u"Amendment", "ecs.core.forms.forms.AmendmentNotificationForm", True, False, u"Die Kommission stimmt der vorgeschlagenen Protokolländerung zu."),
    )

    for name, form, diff, vote_ext, default_response in types:
        t, created = NotificationType.objects.get_or_create(name=name)
        update_instance(t, {
            'form': form,
            'diff': diff,
            'default_response': default_response,
            'grants_vote_extension': vote_ext,
        })

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def notification_workflow():
    from ecs.notifications.workflow import (InitialNotificationReview, EditNotificationAnswer, AutoDistributeNotificationAnswer, SignNotificationAnswer, 
        needs_executive_review, is_susar, is_report, is_amendment)

    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    NOTIFICATION_REVIEW_GROUP = 'EC-Notification Review Group'
    SIGNING_GROUP = 'EC-Signing Group'

    setup_workflow_graph(Notification,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name=_('Start')),
            'susar_review': Args(EditNotificationAnswer, group=OFFICE_GROUP, name=_('Susar Review')),
            'initial_notification_review': Args(InitialNotificationReview, group=OFFICE_GROUP, name=_('Initial Notification Review')),
            'initial_amendment_review': Args(InitialNotificationReview, group=OFFICE_GROUP, name=_('Initial Amendment Review')),
            'notification_group_review': Args(EditNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP, name=_('Notification Review')),
            'executive_group_review': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP, name=_('Notification Review')),
            'notification_answer_signing': Args(SignNotificationAnswer, group=SIGNING_GROUP, name=_('Notification Answer Signing')),
            'distribute_notification_answer': Args(AutoDistributeNotificationAnswer, name=_('Distribute Notification Answer')),
        },
        edges={
            ('start', 'susar_review'): Args(guard=is_susar),
            ('start', 'initial_notification_review'): Args(guard=is_report),
            ('start', 'initial_amendment_review'): Args(guard=is_amendment),

            ('initial_notification_review', 'notification_group_review'): Args(guard=needs_executive_review, negated=True),
            ('initial_notification_review', 'executive_group_review'): Args(guard=needs_executive_review),
            ('initial_amendment_review', 'notification_group_review'): Args(guard=needs_executive_review, negated=True),
            ('initial_amendment_review', 'executive_group_review'): Args(guard=needs_executive_review),

            ('executive_group_review', 'notification_answer_signing'): None,

            ('susar_review', 'distribute_notification_answer'): None,
            ('notification_group_review', 'distribute_notification_answer'): None,
            ('notification_answer_signing', 'distribute_notification_answer'): None,
        }
    )
