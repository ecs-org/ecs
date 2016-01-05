# -*- coding: utf-8 -*-
import re
import textwrap
from HTMLParser import HTMLParser

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives, make_msgid
from django.utils.html import strip_tags


def html2text(htmltext):
    text = HTMLParser().unescape(strip_tags(htmltext))
    text = '\n\n'.join(re.split(r'\s*\n\s*\n\s*', text))
    text = re.sub('\s\s\s+', ' ', text)
    wrapper = textwrap.TextWrapper(
        replace_whitespace=False, drop_whitespace=False, width=72)
    return '\n'.join(wrapper.wrap(text))


def create_mail(subject, message, from_email, recipient, message_html=None, \
                attachments= None, msgid=None, rfc2822_headers=None):
    headers = {'Message-ID': msgid or make_msgid()}

    if rfc2822_headers:
        headers.update(rfc2822_headers)

    if message is None: # make text version out of html if text version is missing
        message = html2text(message_html)
    
    if message_html:
        msg = EmailMultiAlternatives(subject, message, from_email, [recipient],
            headers=headers)
        msg.attach_alternative(message_html, "text/html")
    else:
        msg = EmailMessage(subject, message, from_email, [recipient],
            headers=headers)
      
    if attachments:
        for filename, content, mimetype in attachments:
            msg.attach(filename, content, mimetype)
            
    return msg

    
def deliver(recipient_list, *args, **kwargs):
    '''
    send email to recipient list
    returns a list of (msgid, rawmessage) for each messages to be sent
    '''
    # make a list if only one recipient (and therefore string) is there
    if isinstance(recipient_list, basestring):
        recipient_list = [recipient_list]
 
    sentids = []
    for recipient in recipient_list:
        sentids.append(deliver_to_recipient(recipient, *args, **kwargs))

    return sentids


def deliver_to_recipient(recipient, subject, message, from_email, \
                         message_html=None, attachments=None, \
                         msgid=None, nofilter=False, rfc2822_headers=None, \
                         **kwargs):
    if msgid is None:
        msgid = make_msgid()

    msg = create_mail(subject, message, from_email, recipient, message_html, \
                      attachments, msgid, rfc2822_headers)
    
    backend = None
    if settings.ECSMAIL.get('filter_outgoing_smtp') and not nofilter:
        backend = settings.LIMITED_EMAIL_BACKEND

    connection = mail.get_connection(backend= backend)
    connection.send_messages([msg])
    
    return (msgid, msg.message(),)
