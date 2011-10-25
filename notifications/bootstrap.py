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
        dict(
            name = u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", 
            form = "ecs.notifications.forms.SusarNotificationForm",
            default_response = u"Die Kommission nimmt diese Meldung ohne Einspruch zur Kenntnis.",
            includes_diff = False,
            grants_vote_extension = False,
            is_rejectable = False,
            finishes_study = False,
        ),
        dict(
            name = u"Zwischenbericht",
            form = "ecs.notifications.forms.ProgressReportNotificationForm",
            default_response = u"",
            includes_diff = False,
            grants_vote_extension = True,
            is_rejectable = True,
            finishes_study = False,
        ),
        dict(
            name = u"Abschlussbericht",
            form = "ecs.notifications.forms.CompletionReportNotificationForm",
            default_response = u"",
            includes_diff = False,
            grants_vote_extension = False,
            is_rejectable = True,
            finishes_study = True,
        ),
        dict(
            name = u"Amendment",
            form = "ecs.notifications.forms.AmendmentNotificationForm",
            default_response = u"Die Kommission stimmt der vorgeschlagenen Protokolländerung zu.",
            includes_diff = True,
            grants_vote_extension = False,
            is_rejectable = True,
            finishes_study = False,
        ),
    )

    for data in types:
        data = data.copy()
        t, created = NotificationType.objects.get_or_create(name=data.pop('name'), defaults=data)
        update_instance(t, data)

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def notification_workflow():
    from ecs.notifications.workflow import (InitialNotificationReview, InitialAmendmentReview, EditNotificationAnswer, AutoDistributeNotificationAnswer, SignNotificationAnswer, 
        needs_executive_review, is_susar, is_report, is_amendment, needs_further_review)

    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    NOTIFICATION_REVIEW_GROUP = 'EC-Notification Review Group'
    SIGNING_GROUP = 'EC-Signing Group'

    setup_workflow_graph(Notification,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name=_('Start')),
            'susar_review': Args(EditNotificationAnswer, group=OFFICE_GROUP, name=_('Susar Review')),
            'notification_answer_signing': Args(SignNotificationAnswer, group=SIGNING_GROUP, name=_('Notification Answer Signing')),
            'distribute_notification_answer': Args(AutoDistributeNotificationAnswer, name=_('Distribute Notification Answer')),

            # reports
            'office_group_review': Args(EditNotificationAnswer, group=OFFICE_GROUP, name=_('Notification Review')),
            'executive_group_review': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP, name=_('Notification Review')),

            # amendments
            'initial_amendment_review': Args(InitialAmendmentReview, group=OFFICE_GROUP, name=_('Initial Amendment Review')),
            'notification_group_review': Args(EditNotificationAnswer, group=NOTIFICATION_REVIEW_GROUP, name=_('Amendment Review')),
            'executive_amendment_review': Args(EditNotificationAnswer, group=EXECUTIVE_GROUP, name=_('Amendment Review')),
        },
        edges={
            ('start', 'susar_review'): Args(guard=is_susar),
            ('start', 'office_group_review'): Args(guard=is_report),
            ('start', 'initial_amendment_review'): Args(guard=is_amendment),

            # reports
            ('office_group_review', 'executive_group_review'): None,
            ('executive_group_review', 'office_group_review'): Args(guard=needs_further_review),
            ('executive_group_review', 'distribute_notification_answer'): Args(guard=needs_further_review, negated=True),

            # amendments
            ('initial_amendment_review', 'notification_group_review'): Args(guard=needs_executive_review, negated=True),
            ('initial_amendment_review', 'executive_amendment_review'): Args(guard=needs_executive_review),

            ('notification_group_review', 'executive_amendment_review'): Args(guard=needs_further_review), 
            ('notification_group_review', 'distribute_notification_answer'): Args(guard=needs_further_review, negated=True),

            ('executive_amendment_review', 'notification_group_review'): Args(guard=needs_further_review),
            ('executive_amendment_review', 'notification_answer_signing'): Args(guard=needs_further_review, negated=True),
            ('notification_answer_signing', 'distribute_notification_answer'): None,

            ('susar_review', 'distribute_notification_answer'): None,
            
        }
    )
