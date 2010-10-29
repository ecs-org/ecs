# -*- coding: utf-8 -*-

import re
from time import gmtime, strftime
from email.Utils import make_msgid

from django.conf import settings
from django.core.mail import get_connection

from lamson import routing
from lamson.mail import MailRequest, MailResponse

from ecs.utils.testcases import EcsTestCase
from ecs.ecsmail.mail import send_mail


class MailTestCase(EcsTestCase):
    '''
    TestCase Class, for testing Mail
    if you play with receive, you probably want to "from lamson.server import SMTPError" inside your tests, to check for smtperrorcodes
    '''
    @classmethod
    def setUpClass(self):      
        # permit emails sent to all
        self.saved_EMAIL_WHITELIST = settings.EMAIL_WHITELIST
        settings.EMAIL_WHITELIST =[]
              
        #  import lamson ecsmail config, this makes the production frontend accessable from within the testcase
        import ecs.ecsmail.mailconf as lamson_settings

    @classmethod
    def teardownClass(self):
        settings.EMAIL_WHITELIST = self.saved_EMAIL_WHITELIST

    def setUp(self):
        routing.Router.clear_states()
        self.connection = get_connection()  # get django default mailbackend 
        super(MailTestCase, self).setUp()

    def tearDown(self):
        super(MailTestCase, self).tearDown()
        
    @classmethod
    def queue_clear(self):
        self.connection.outbox = []
        
    @classmethod
    def queue_count(self):
        return len(self.connection.outbox) if hasattr(self.connection, "outbox") else 0
    
    @classmethod
    def queue_list(self):
        return self.connection.outbox if hasattr(self.connection, "outbox") else []
    
    @classmethod
    def queue_get(self, key):
        if not hasattr(self.connection, "outbox"): 
            raise KeyError("Empty Outbox")
        else:
            return self.connection.outbox [key]
    
    @classmethod
    def deliver(self, To, From, Subject, Body):
        ''' just call our standard email deliver '''
        send_mail(Subject, Body, From, To)
        
    @classmethod
    def receive(self, To, From, Subject, Body):
        ''' Fakes an incoming message trough ecsmail server '''
        messageid = make_msgid()
        sample = MailResponse(To=To, From=From, Subject=Subject, Body=Body)
        sample['Date'] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        sample['Message-ID'] = messageid
        msg = MailRequest('localhost', sample['From'], sample['To'], str(sample))
        routing.Router.deliver(msg)

    @classmethod
    def is_delivered(self, pattern):
        ''' returns message that matches the regex (searched = msgbody), or False if not found '''
        regp = re.compile(pattern)
        if not hasattr(self.connection, "outbox"):
            return False # empty outbox, so pattern does not match
        
        for key, msg in enumerate(self.connection.outbox):
            if regp.search(str(msg)):
                return msg
    
        return False # didn't find anything

    
