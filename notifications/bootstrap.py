from ecs import bootstrap
from ecs.notifications.models import NotificationType


@bootstrap.register()
def notification_types():
    types = (
        (u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", "ecs.core.forms.MultiNotificationForm", False),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm", False),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm", False),
        (u"Amendment", "ecs.core.forms.forms.AmendmentNotificationForm", True),
    )
    
    for name, form, diff in types:
        NotificationType.objects.get_or_create(name=name, form=form, diff=diff)
