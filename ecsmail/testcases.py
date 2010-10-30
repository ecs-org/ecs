# -*- coding: utf-8 -*-

import re

import django.core.mail
from django.conf import settings
from django.core.mail import make_msgid

from lamson import routing
from lamson.mail import MailRequest

from ecs.utils.testcases import EcsTestCase
from ecs.ecsmail.mail import deliver as ecsmail_deliver
from ecs.ecsmail.mail import create_mail


class MailTestCase(EcsTestCase):
    '''
    TestCase Class, for testing Mail inside the ecs environment
    if you play with self.receive, you probably want to "from lamson.server import SMTPError" inside your tests,
    to check for smtperrorcodes
    '''
    @classmethod
    def setUpClass(self):    
        # permit emails sent to all
        self.saved_EMAIL_WHITELIST = settings.EMAIL_WHITELIST
        settings.EMAIL_WHITELIST =[]
        
        super(MailTestCase, self).setUpClass()      
        #  import lamson ecsmail config, this makes the production frontend accessable from within the testcase
        import ecs.ecsmail.mailconf as lamson_settings

    @classmethod
    def teardownClass(self):
        settings.EMAIL_WHITELIST = self.saved_EMAIL_WHITELIST
        super(MailTestCase, self).teardownClass()

    def setUp(self):
        routing.Router.clear_states()
        self.queue_clear()
        super(MailTestCase, self).setUp()

    def tearDown(self):
        super(MailTestCase, self).tearDown()
        
    @staticmethod
    def _entry_transform(entry):
        return unicode(entry.message())
    
    @classmethod
    def queue_clear(self):
        django.core.mail.outbox = []
        
    @classmethod
    def queue_count(self):
        return len(django.core.mail.outbox) if hasattr(django.core.mail, "outbox") else 0
    
    @classmethod
    def queue_list(self):
        if hasattr(django.core.mail, "outbox"):
            return [self._entry_transform(x) for x in django.core.mail.outbox]
        else:
            return []
    
    @classmethod
    def queue_get(self, key):
        if not hasattr(django.core.mail, "outbox"): 
            raise KeyError("Empty Outbox")
        else:
            return self._entry_transform(django.core.mail.outbox [key])
    
    @classmethod
    def deliver(self, subject, message, from_email, recipient_list, message_html=None, attachments=None, callback=None):
        ''' just call our standard email deliver '''
        return ecsmail_deliver(subject, message, from_email, recipient_list, message_html, attachments, callback)
        
    @classmethod
    def receive(self, subject, message, from_email, recipient_list, message_html=None, attachments=None, ):
        ''' Fakes an incoming message trough ecsmail server '''
        if isinstance(recipient_list, basestring):
            recipient_list = [recipient_list]

        sentids = []
        for recipient in recipient_list:
            msgid = make_msgid()
            msg = create_mail(subject, message, from_email, recipient, message_html, attachments, msgid)
            routing.Router.deliver(MailRequest('localhost', from_email, recipient, str(msg.message())))
            sentids += [[msgid, msg.message()]]
            
        return sentids
    
    @classmethod
    def is_delivered(self, pattern):
        ''' returns message that matches the regex (searched = msgbody), or False if not found '''
        regp = re.compile(pattern)
        if self.queue_count() == 0:
            return False # empty outbox, so pattern does not match
        
        for msg in self.queue_list():
            if regp.search(str(msg)):
                return msg
    
        return False # didn't find anything
