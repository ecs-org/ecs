# -*- coding: utf-8 -*-
from ecs import bootstrap
from ecs.notifications.models import NotificationType, Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.utils import Args

@bootstrap.register()
def notification_types():
    types = (
        (u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", "ecs.core.forms.MultiNotificationForm", False, False, u"Die Komission nimmt diese Meldung ohne Einspruch zur Kenntnis."),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm", False, True, u""),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm", False, True, u""),
        (u"Amendment", "ecs.core.forms.forms.AmendmentNotificationForm", True, True, u"Die Komission stimmt der vorgeschlagenen Protokolländerung zu."),
    )
    
    for name, form, diff, earfa, default_response in types:
        t, created = NotificationType.objects.get_or_create(name=name, form=form, diff=diff)
        changed = False
        if t.executive_answer_required_for_amg != earfa:
            t.executive_answer_required_for_amg = earfa
            changed = True
        if t.default_response != default_response:
            t.default_response = default_response
            changed = True
        if changed:
            t.save()


@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def notification_workflow():
    from ecs.notifications.workflow import (EditNotificationAnswer, DistributeNotificationAnswer, SignNotificationAnswer, 
        needs_executive_answer, is_amendment, is_valid_amendment)

    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    NOTIFICATION_REVIEW_GROUP = 'EC-Notification Review Group'

    setup_workflow_graph(Notification,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name="Start"),
            'initial_amendment_review': Args(EditNotificationAnswer, group=OFFICE_GROUP),
            'regular_review': Args(Generic),
            'notification_answer': Args(EditNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP),
            'executive_notification_answer': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP),
            'sign_notification_answer': Args(SignNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP),
            'sign_executive_notification_answer': Args(SignNotificationAnswer, group=EXECUTIVE_GROUP),
            'distribute_notification_answer': Args(DistributeNotificationAnswer, group=OFFICE_GROUP, end=True),
        },
        edges={
            ('start', 'initial_amendment_review'): Args(guard=is_amendment),
            ('start', 'regular_review'): Args(guard=is_amendment, negated=True),
            ('initial_amendment_review', 'regular_review'): Args(guard=is_valid_amendment),
            ('initial_amendment_review', 'sign_notification_answer'): Args(guard=is_valid_amendment, negated=True),
            ('regular_review', 'notification_answer'): Args(guard=needs_executive_answer, negated=True),
            ('regular_review', 'executive_notification_answer'): Args(guard=needs_executive_answer),
            ('notification_answer', 'sign_notification_answer'): None,
            ('executive_notification_answer', 'sign_executive_notification_answer'): None,
            ('sign_notification_answer', 'distribute_notification_answer'): None,
            ('sign_executive_notification_answer', 'distribute_notification_answer'): None,
        }
    )
