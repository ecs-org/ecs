from celery.decorators import task
from django.conf import settings
import logging

@task()
def queued_mail_send(message, To, From, **kwargs):
    logger = queued_mail_send.get_logger(**kwargs)
    logger.info("".join(("queued mail deliver using ", str(relay), ", from ", From, ", to ", To, ", msg ", repr(message))))
    # FIXME new code to finally send message
    # FIXME needs errror handling and return value 
