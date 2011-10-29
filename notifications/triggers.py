from ecs.notifications import signals
from ecs.utils import connect 

@connect(signals.on_notification_submit)
def on_notification_submit(sender, **kwargs):
    notification = kwargs['notification']
    notification.render_pdf()