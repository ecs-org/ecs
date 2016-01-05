# -*- coding: utf-8 -*-
import os
import mimetypes
import re
import textwrap
from HTMLParser import HTMLParser

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, make_msgid
from django.utils.html import strip_tags

from ecs.ecsmail.tasks import queued_mail_send


def html2text(htmltext):
    text = HTMLParser().unescape(strip_tags(htmltext))
    text = '\n\n'.join(re.split(r'\s*\n\s*\n\s*', text))
    text = re.sub('\s\s\s+', ' ', text)
    wrapper = textwrap.TextWrapper(
        replace_whitespace=False, drop_whitespace=False, width=72)
    return '\n'.join(wrapper.wrap(text))


def create_mail(subject, message, from_email, recipient, message_html=None, \
                attachments= None, msgid=None, rfc2822_headers=None, **kwargs):
    '''
    '''
    if msgid is None:
        msgid = make_msgid()
    headers = {'Message-ID': msgid}
    
    if type(rfc2822_headers) is dict:
        for head_key in rfc2822_headers.keys():
            headers[head_key]=rfc2822_headers[head_key]

    if message is None: # make text version out of html if text version is missing
        message = html2text(message_html)
    
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

    
def deliver(recipient_list, *args, **kwargs):
    """
    send email to recipient list, puts messages to send into celery queue
    returns a list of (msgid, rawmessage) for each messages to be sent
    if callback is set to a celery task:
       it will be called on every single recipient delivery with callback(msgid, status)
    """
    # make a list if only one recipient (and therefore string) is there
    if isinstance(recipient_list, basestring):
        recipient_list = [recipient_list]
 
    sentids = []
    for recipient in recipient_list:
        sentids.append(deliver_to_recipient(recipient, *args, **kwargs))

    return sentids


def deliver_to_recipient(recipient, subject, message, from_email, \
                         message_html=None, attachments=None, callback=None, \
                         msgid=None, nofilter=False, rfc2822_headers=None, \
                         **kwargs):
    if msgid is None:
        msgid = make_msgid()

    msg = create_mail(subject, message, from_email, recipient, message_html, \
                      attachments, msgid, rfc2822_headers)
    
    backend = None
    if settings.ECSMAIL.get('filter_outgoing_smtp') and not nofilter:
        backend = settings.LIMITED_EMAIL_BACKEND
    
    queued_mail_send.apply_async(args=[msgid, msg, from_email, recipient, callback, backend], countdown=3)
    return (msgid, msg.message(),)
