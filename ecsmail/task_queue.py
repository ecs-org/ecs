from celery.decorators import task
from django.conf import settings
import logging

@task(max_retries= 3)
def queued_mail_send(msgid, message, To, From, callback=None, **kwargs):
    logger = queued_mail_send.get_logger(**kwargs)
    logger.debug("queued mail deliver id %s, from %s, to %s, callback %s, msg %s" %
                (msgid, From, To, str(callback), repr(message)))
    
    state = "pending"
    
    if callback:
        subtask(callback).delay(msgid, state)
        
    try:
        pass # fixme code to send msg
    except Exception as exc:
        if callback:
            subtask(callback).delay(msgid, "retry")
        queued_mail_send.retry(exc=exc)
        

    # fixme: set success result
    if callback:
        subtask(callback).delay(msgid, "success")
        
