# -*- coding: utf-8 -*-

import os
import logging
import mimetypes

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, make_msgid

from ecs.ecsmail.persil import whitewash
from ecs.ecsmail.task_queue import queued_mail_send
   

def create_mail(subject, message, from_email, recipient, message_html=None, attachments= None, msgid=None, **kwargs):
    '''
    '''
    if msgid is None:
        msgid = make_msgid()
    headers = {'Message-ID': msgid}
    
    if message is None: # make text version out of html if text version is missing
        message = whitewash(message_html)
    
    if message and message_html:
        msg = EmailMultiAlternatives(subject, message, from_email, [recipient], headers= headers)
        msg.attach_alternative(message_html, "text/html")
    else:
        msg = EmailMessage(subject, message, from_email, [recipient], headers= headers)
      
    if attachments:
        for attachment in attachments:
            filename = content = mimetype = encoding = None
            
            if isinstance(attachment, tuple) or isinstance(attachment, list):
                filename, content = attachment[0:2]
                if len(attachment) == 3:
                    mimetype = attachment[2]
                else:
                    mimetype, encoding = mimetypes.guess_type(filename)
            elif isinstance(attachment, basestring):
                filename = attachment
                if not os.path.exists(filename):
                    raise IOError("attachment file not found %s" % filename)
                mimetype, encoding = mimetypes.guess_type(filename)    
                content = open(filename, "rb").read()
            else:
                raise TypeError('dont know how to handle attachment from type %s' % (str(type(attachment))))

            if not mimetype:
                raise TypeError("No content type given, and couldn't guess from the filename: %s" % filename)
                
            msg.attach(filename, content, mimetype)
            
    return msg

    
def deliver(subject, message, from_email, recipient_list, message_html=None, attachments= None, callback=None, **kwargs):
    """
    send email to recipient list (filter them through settings.EMAIL_WHITELIST if exists), 
    puts messages to send into celery queue
    returns a list of (msgid, rawmessage) for each messages to be sent
    if callback is set to a celery task:
       it will be called on every single recipient delivery with callback(msgid, status)
    """
    # make a list if only one recipient (and therefore string) is there
    if isinstance(recipient_list, basestring):
        recipient_list = [recipient_list]
 
    # filter out recipients which are not in the whitelist
    mylist = set(recipient_list)
    bad = None
    if hasattr(settings, "EMAIL_WHITELIST") and settings.EMAIL_WHITELIST:
        bad = set([x for x in recipient_list if x not in settings.EMAIL_WHITELIST])
    if bad:
        logger = logging.getLogger()
        logger.warning('BAD EMAILS: %s are bad out of %s' % (str(bad), str(mylist)))
        recipient_list = list(mylist - bad)

    sentids = []
    for recipient in recipient_list:
        msgid = make_msgid()
        msg = create_mail(subject, message, from_email, recipient, message_html, attachments, msgid)
        
        queued_mail_send.apply_async(args=[msgid, msg, from_email, recipient, callback], countdown=3)
        #queued_mail_send(msgid, msg, from_email, recipient, callback)
        sentids += [[msgid, msg.message()]]
    return sentids


def send_mail(subject, message, from_email, recipient_list, message_html=None, attachments=None, callback=None, **kwargs):
    raise(DeprecationWarning('deprecated, use deliver for sending emails'))
    return deliver(subject, message, from_email, recipient_list, message_html, attachments, callback)


def send_html_email(subject, message_html, recipient_list, from_email=settings.DEFAULT_FROM_EMAIL, attachments=None, callback=None, **kwargs):
    raise(DeprecationWarning('deprecated, use deliver with message=None, message_html= htmltext for sending emails'))
    return deliver(subject, None, from_email, recipient_list, message_html, attachments, callback)
