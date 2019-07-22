import re
import textwrap
from html.parser import HTMLParser

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


def create_mail(subject, message, from_email, recipient, message_html=None,
                attachments=None, rfc2822_headers=None):

    from ecs.core.models import AdvancedSettings

    headers = {'Message-ID': make_msgid(domain=settings.DOMAIN)}
    if from_email == settings.DEFAULT_FROM_EMAIL:
        # if empty, set Auto-Submitted and Reply-To for mails from DEFAULT_FROM_EMAIL
        if not rfc2822_headers or not rfc2822_headers.get('Auto-Submitted', None):
            headers.update({'Auto-Submitted': 'auto-generated'})
        if not rfc2822_headers or not rfc2822_headers.get('Reply-To', None):
            headers.update({'Reply-To': AdvancedSettings.objects.get(pk=1).default_contact})

    if rfc2822_headers:
        headers.update(rfc2822_headers)

    if message is None:  # make text version out of html if text version is missing
        message = html2text(message_html)

    if message_html:
        msg = EmailMultiAlternatives(subject, message, from_email, [recipient], headers=headers)
        msg.attach_alternative(message_html, "text/html")
    else:
        msg = EmailMessage(subject, message, from_email, [recipient], headers=headers)

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
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]

    sentids = []
    for recipient in recipient_list:
        sentids.append(deliver_to_recipient(recipient, *args, **kwargs))

    return sentids


def deliver_to_recipient(recipient, subject, message, from_email,
    message_html=None, attachments=None, nofilter=False, rfc2822_headers=None):

    msg = create_mail(subject, message, from_email, recipient,
                      message_html, attachments, rfc2822_headers)
    msgid = msg.extra_headers['Message-ID']

    backend = settings.EMAIL_BACKEND
    if (nofilter or recipient.split('@')[1] in settings.EMAIL_UNFILTERED_DOMAINS or
            recipient in settings.EMAIL_UNFILTERED_INDIVIDUALS):
        backend = settings.EMAIL_BACKEND_UNFILTERED

    connection = mail.get_connection(backend=backend)
    connection.send_messages([msg])

    return (msgid, msg.message(),)
