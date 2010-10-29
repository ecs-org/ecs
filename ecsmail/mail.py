# -*- coding: utf-8 -*-

import logging
from time import gmtime, strftime
from email.Utils import make_msgid

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from lamson import encoding
from lamson.mail import MailResponse

from ecs.ecsmail.task_queue import queued_mail_send


def __parse_attachments(attachments):
    ''' 
    takes iterable of either filenamestrings, or list/tuples of (filename, data [,content_type])
    returns tuples of filename, data, content_type
    '''
    import mimetypes
    if attachments:
        for attachment in attachments:
            filename = data = content_type = encoding = None
            
            if isinstance(attachment, tuple) or isinstance(attachment, list):
                filename, data = attachment[0:2]
                if len(attachment) == 3:
                    content_type = attachment[2]
                else:
                    content_type, encoding = mimetypes.guess_type(filename)
            elif isinstance(attachment, basestring):
                content_type, encoding = mimetypes.guess_type(filename)
                assert content_type, "No content type given, and couldn't guess from the filename: %r" % filename
            else:
                assert TypeError('dont know how to handle attachment from type %s' % (str(type(attachment))))

            yield (filename, data, content_type)


def __to_message(message):
    '''
    transform message object to ready to use rfc compliant message
    '''
    del message.base.parts[:] 
  
    if message.Body and message.Html:
        #FIXME: we are killing the plain body if both plain and html are there, but this is wrong, but multipart/alternative doesnt display attachments right
        message.Body = None
        #message.multipart = True 
        #if len(message.attachments) != 0:   # FIXME: this is a hack, but i think it works
        #    message.base.content_encoding['Content-Type'] = ('multipart/mixed', {}) 
        #else:
        #   message.base.content_encoding['Content-Type'] = ('multipart/alternative', {}) 
    if message.multipart: 
        message.base.body = None 
        if message.Body: 
            message.base.attach_text(message.Body, 'text/plain')   
        if message.Html: 
            message.base.attach_text(message.Html, 'text/html') 
        for args in message.attachments: 
            message._encode_attachment(**args) 
    elif message.Body: 
        message.base.body = message.Body 
        message.base.content_encoding['Content-Type'] = ('text/plain', {}) 
    elif message.Html: 
        message.base.body = message.Html 
        message.base.content_encoding['Content-Type'] = ('text/html', {}) 
   
    return encoding.to_message(message.base)             


def send_mail(subject, message, from_email, recipient_list, message_html=None, attachments=None, callback=None, **kwargs):
    '''
    send email to recipient list (filter them through settings.EMAIL_WHITELIST if exists), 
    puts messages to send into celery queue
    returns a list of (messageid, rawmessage) for each messages to be sent
    if callback is set to a celery task:
       it will be called on every single recipient delivery with callback(msgid, status)
    '''
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
        messageid = make_msgid()
        mess = MailResponse(To=recipient, From=from_email, Subject=subject, Body=message, Html=message_html)
        if attachments:
            for filename, data, content_type in __parse_attachments(attachments):
                mess.attach(filename=filename, content_type=content_type, data=data)              
        mess['Date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        mess['Message-ID'] = messageid
        mess = __to_message(mess)

        # for each recipient, make one entry in the queue 
        queued_mail_send.apply_async(args=[messageid, mess, recipient, from_email], countdown=3) # , callback
        sentids += [[messageid, mess]]
    return sentids


def send_html_email(subject, message_html, recipient_list, from_email=settings.DEFAULT_FROM_EMAIL, attachments=None, callback=None, **kwargs):
    from ecs.ecsmail.persil import whitewash
    message = whitewash(message_html)
    kwargs.setdefault('fail_silently', False)
    return send_mail(subject, message, from_email, recipient_list, message_html, attachments=attachments, callback=callback, **kwargs)
