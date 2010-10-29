from celery.decorators import task
from celery.task.sets import subtask
from celery.exceptions import MaxRetriesExceededError

from django.conf import settings
from django.core import mail
import logging

@task() # (max_retries= 3)
def queued_mail_send(msgid, message, To, From, callback=None, **kwargs):
    logger = queued_mail_send.get_logger(**kwargs)
    logger.debug("queued mail deliver id %s, from %s, to %s, callback %s, msg %s" %
                (msgid, From, To, str(callback), repr(message)))

    if callback:
        subtask(callback).delay(msgid, "pending")
    
    try:
        connection = mail.get_connection()
        connection.send_messages(list(message))
    except Exception as exc:
        """
        if callback:
            subtask(callback).delay(msgid, "retry")
        try:
            queued_mail_send.retry(exc=exc)
        except MaxRetriesExceededError:
        """
        if callback:
            subtask(callback).delay(msgid, "failure")
            return

    if callback:
        subtask(callback).delay(msgid, "success")
        
