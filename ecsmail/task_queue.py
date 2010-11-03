import logging

from celery.decorators import task
from celery.task.sets import subtask
from celery.exceptions import MaxRetriesExceededError

from django.conf import settings
from django.core import mail

@task() # (max_retries= 3)
def queued_mail_send(msgid, msg, from_email, recipient, callback=None, **kwargs):
    logger = queued_mail_send.get_logger(**kwargs)
    logger.debug("queued mail deliver id %s, from %s, to %s, callback %s, msg %s" %
                (msgid, from_email, recipient, str(callback), repr(msg)))

    if callback:
        subtask(callback).delay(msgid, "started")
    
    try:
        connection = mail.get_connection()
        connection.send_messages([msg])
    except Exception as exc:
        logger.error(str(exc))
        if callback:
            subtask(callback).delay(msgid, "failure")
        raise
        # FIXME: retry does not work, the way i think it should work
        """
        if callback:
            subtask(callback).delay(msgid, "retry")
        try:
            queued_mail_send.retry(exc=exc)
        except MaxRetriesExceededError:
        """
        
    if callback:
        subtask(callback).delay(msgid, "success")
        
