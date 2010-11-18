from django.conf import settings
from celery.decorators import task
   
@task()
def update_smtp_delivery(msgid, state, **kwargs):
    logger = update_smtp_delivery.get_logger(**kwargs)
    logger.info("updating status of msg %s to %s" % (msgid, state))

    from ecs.communication.models import Message
    try:
        Message.objects.get(rawmsg_msgid = msgid).update(smtp_delivery_state = state)        
    except Exception as exc:
        logger.error("could not update status of message id %s, exception was %r" % (msgid, exc))
