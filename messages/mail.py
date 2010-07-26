import os
import mimetypes
from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.mail import EmailMessage, EmailMultiAlternatives
from time import gmtime, strftime

def __parse_attachments(attachments):
    ''' takes iterable of either filenamestrings, or list/tuples of (filename, data [,content_type])
        returns tuples of filename, data, content_type '''  
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

            
def django_send_mail(subject, message, from_email, recipient_list, fail_silently=False,
                            message_html=None, attachments=None,
                            auth_user=None, auth_password=None, connection=None, 
                            **kwargs):
    
    print 'DJANGO SEND MAIL'
    subject = force_unicode(subject)
    message = force_unicode(message)
    bcc = None
    headers = None

    email = EmailMultiAlternatives(subject=subject, body=message, from_email=from_email,
                to=recipient_list, bcc=bcc, headers=headers)
    if message_html:
        email.attach_alternative(message_html, "text/html")  
    if attachments:
        for filename, data, content_type in __parse_attachments(attachments):
            if data:
                email.attach(filename=os.path.basename(filename), content=data, mimetype=content_type)
            else:
                email.attach_file(filename)
    email.send()

            
def lamson_send_mail(subject, message, from_email, recipient_list, fail_silently=False,
                        message_html=None, attachments=None, **kwargs):
    '''
        sends message and returns messageid of message sent
    '''
    from ecs.ecsmail.config.boot import relay
    from lamson.mail import MailResponse
    from email.Utils import make_msgid
    print 'LAMSON SEND MAIL'
    for recipient in recipient_list:
        messageid = make_msgid()
        mess = MailResponse(To=recipient, From=from_email, Subject=subject, Body=message, Html=message_html)
        if attachments:
            for filename, data, content_type in __parse_attachments(attachments):
                mess.attach(filename=filename, content_type=content_type, data=data)
                
        mess['Date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        mess['Message-ID'] = messageid
        mess = mess.to_message()
        relay.deliver(mess, To=recipient, From=from_email)
        return messageid


def send_mail(**kwargs):
    '''
        send email to recipient list (filter them through settings.EMAIL_WHITELIST if exists), and return message-id of sent message
    '''
    mylist = set(kwargs['recipient_list'])
    bad = None
    if settings.EMAIL_WHITELIST:
        bad = set([x for x in kwargs['recipient_list'] if x not in settings.EMAIL_WHITELIST])
    if bad:
        print 'BAD EMAILS:', mylist, bad
        kwargs['recipient_list'] = list(mylist - bad)
        
    return lamson_send_mail(**kwargs)
    