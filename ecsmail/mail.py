from django.conf import settings

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
            
def lamson_send_mail(subject, message, from_email, recipient_list, fail_silently=False,
                        message_html=None, attachments=None, **kwargs):
    '''
    puts messages to send into celery queue and returns list of messageids of messages to be sent
    '''
    from lamson.mail import MailResponse
    from email.Utils import make_msgid
    from time import gmtime, strftime
    from ecs.ecsmail.task_queue import queued_mail_send
    sentids = []

    # XXX: make a list if only one recipient (and therefore string) is there
    if isinstance(recipient_list, basestring):
        recipient_list = [recipient_list]

    for recipient in recipient_list:
        messageid = make_msgid()
        mess = MailResponse(To=recipient, From=from_email, Subject=subject, Body=message, Html=message_html)
        if attachments:
            for filename, data, content_type in __parse_attachments(attachments):
                mess.attach(filename=filename, content_type=content_type, data=data)              
        mess['Date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        mess['Message-ID'] = messageid
        mess = mess.to_message()
        queued_mail_send.delay(mess, To=recipient, From=from_email)
        sentids += messageid
    return sentids


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
