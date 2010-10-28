from celery.decorators import task
from ecs.communication.models import Message

@task()
def update_smtp_delivery(msgid, state, **kwargs):
    logger = update_smtp_delivery.get_logger(**kwargs)
    logger.info("updating status of msg %s to %s" % (msgid, state))

    try:
        Message.objects.get(raw_msgid = msgid).update(smtp_delivery_state = state)        
    except Exception as exc:
        logger.Error("could not update status of message id %s, exception was %s" % (msgid, str(exc)))
