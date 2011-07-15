# -*- coding: utf-8 -*-

import os
import logging
import mimetypes
import re
import copy

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, make_msgid

import BeautifulSoup
from BeautifulCleaner.bc import Cleaner, removeElement

from ecs.ecsmail.tasks import queued_mail_send
   


class TotalCleaner(Cleaner):
    style = True
    whitelist_tags = set([])

# http://code.activestate.com/recipes/148061/
def _wrap(text, width):
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def whitewash(htmltext, puretext=True):
    ''' cleans htmltext into harmless pure text '''
    if puretext:
        hexentityMassage = copy.copy(BeautifulSoup.BeautifulSoup.MARKUP_MASSAGE)
        hexentityMassage = [(re.compile('&#x([^;]+);'), 
            lambda m: '&#%d' % int(m.group(1), 16))]

        doc = BeautifulSoup.BeautifulSoup(htmltext,
            convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES,
            markupMassage=hexentityMassage)        
    else:
        doc = BeautifulSoup.BeautifulSoup(htmltext)
        
    TotalCleaner()(doc) # to kill the really bad tags first.
    for el in doc.findAll():
        removeElement(el)
    string = unicode(doc)
    string = '\n\n'.join(re.split(r'\s*\n\s*\n\s*', string))
    string = re.sub('\s\s\s+', ' ', string)
    string = _wrap(string, 70)
    return string


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


def deliver_to_recipient(recipient, subject, message, from_email, message_html=None, attachments=None, callback=None, msgid=None, **kwargs):
    if msgid is None:
        msgid = make_msgid()

    msg = create_mail(subject, message, from_email, recipient, message_html, attachments, msgid)
    queued_mail_send.apply_async(args=[msgid, msg, from_email, recipient, callback], countdown=3)
    return (msgid, msg.message(),)
