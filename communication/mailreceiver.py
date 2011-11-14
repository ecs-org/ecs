# -*- coding: utf-8 -*-

import logging
import re
import hashlib
import traceback

from socket import gethostbyname

from lamson.routing import route, stateless
from lamson.bounce import bounce_to
from lamson.server import SMTPError

from django.conf import settings
from django.contrib.auth.models import User

from ecs.communication.models import Message
from ecs.ecsmail.utils import deliver_to_recipient, whitewash

@route(".+")
def SOFT_BOUNCE(message):
    __checkConstraints(message)
    prevBounce, ecshash = __findPreviousBounce(message)
    # __logRawMessage(message, ecshash)
    
    # notify users about soft bounces only once
    if prevBounce is None:
        ecsmsg, ecshash = __findInitiatingMessage(message)
        body, attachment_count = __prepareBody(message)
        bouncemsg = ecsmsg.thread.add_message(user=ecsmsg.receiver, text=unicode(body), reply_to=ecsmsg)
        bouncemsg.soft_bounced = True;
        bouncemsg.save()

    return START

@route(".+")
def HARD_BOUNCE(message):
    __checkConstraints(message)
    ecsmsg, ecshash = __findInitiatingMessage(message)
    # __logRawMessage(message, ecshash)
    
    if ecsmsg:
        body, attachment_count = __prepareBody(message)
        ecsmsg.thread.add_message(user=ecsmsg.receiver, text=unicode(body), reply_to=ecsmsg)
    return START

def __findInitiatingMessage(message):
    ecshash = __parseEcsHash(message.To[0])

    if ecshash:
        try:
            ecsmsg = Message.objects.get(uuid=ecshash)
        except Message.DoesNotExist:
            ecsmsg = None
        
        if ecsmsg is None:
            logging.warn('Bogus ecs hash detected. No corresponding message found: %s' % (ecshash))
        else:
            return ecsmsg, ecshash
    
    # Bad destination mailbox address
    raise SMTPError(511)
    
def __findPreviousBounce(message):
    ecsmsg, ecshash = __findInitiatingMessage(message)

    if ecshash:
        try:
            receiver = User.objects.get(email=message.bounce.final_recipient)
            sender = User.objects.get(email=message.From)
            previousBounce = Message.objects.get(thread=ecsmsg.thread, soft_bounced=True, sender=sender, receiver=receiver)
        except:
            previousBounce = None
        
    return previousBounce, ecshash

def __parseEcsHash(address): 
    mat = re.match(r'ecs-([^@]+)', address)
    if mat is not None:
        groups = mat.groups()
        if groups is not None:
            return groups[0]
    else:
        logging.info('Unable to parse ecs hash from address: %s' % (address))        
        return None

def __prepareBody(message):
    attachment_count = 0
    if not message.base.parts:
        body = message.body()
    else:
        body = None
        for part in message.walk():
            if (not body) and ('text/plain' in part.content_encoding['Content-Type']):
                body = part.body
            elif (not body) and ('text/html' in part.content_encoding['Content-Type']):
                body = whitewash(part.body)
            else:
                attachment_count += 1
        if not body:
            body = message.body()

    if attachment_count > 0:
        logging.info('Stripped {0} attachments from mail'.format(attachment_count))

    return (body, attachment_count)

def __stripLongestQuotation(body):
    lines = body.splitlines()
    linecnt = 0
    quoteCnt = 0
    longestRange = [0,0]

    for line in lines:
        if line.startswith('>'):
            quoteCnt+=1
        else:
            if quoteCnt > (longestRange[1] - longestRange[0]):
                longestRange[0] = linecnt - quoteCnt
                longestRange[1] = linecnt
            quoteCnt = 0;
        linecnt+=1

    before = lines[:longestRange[0]]
    after = lines[longestRange[1]:]

    #print "\n".join(before + after)


def __checkConstraints(message):
    if len(message.original) > 1024*1024:
        raise SMTPError(523) # 'Message length exceeds administrative limit.'

@route("(address)@(host)", address=".+")
@bounce_to(soft=SOFT_BOUNCE, hard=HARD_BOUNCE)
@stateless
def START(message, address=None, host=None):
    from ecs.ecsmail.lamson_settings import relay
    __checkConstraints(message)

    if host == settings.ECSMAIL['authoritative_domain']: # we acccept mail for this address
        ecsmsg,ecshash = __findInitiatingMessage(message)

        logging.info('REPLY %s %s %s %s %s' % ( ecshash, ecsmsg, address, host, type(message)))

        body, attachment_count = __prepareBody(message)
        rawmsg = message.to_message().as_string()

        ecsmsg.thread.add_message(ecsmsg.receiver, unicode(body), reply_to=ecsmsg, 
            rawmsg_msgid= message['Message-ID'], rawmsg=rawmsg, 
            rawmsg_digest_hex= hashlib.md5(rawmsg).hexdigest())

        if attachment_count > 0:
            notification_text = '\n'.join([
                "Dear recipient, the Ethics Commission System does not accept e-mail attachments.",
                "{0} attachments have been removed from your message.".format(attachment_count),
                "The message has been delivered as seen below:",
                "",
                "Subject: {0}".format(ecsmsg.thread.subject),
                "{0}".format(unicode(body)),
            ])

            try:
                deliver_to_recipient(
                    message.From,
                    subject='ECS-Mail: Attachment removal notification',
                    message=notification_text,
                    from_email=settings.ECSMAIL['postmaster']
                )
            except:
                traceback.print_exc()

    elif message.Peer[0] in settings.ECSMAIL['trusted_sources']:
        host_addr = gethostbyname(host);
        local_addr = gethostbyname("localhost")

        if host_addr == local_addr:
            pass
            #FIXME which user to notify?
        else:
            logging.info('RELAYING %s %s %s' % (repr(message), address, host))
            relay.deliver(message)
    else:
        raise SMTPError(571) #Delivery not authorized, message refused

