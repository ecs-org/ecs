# -*- coding: utf-8 -*-

from django.conf import settings
from lamson.testing import Queue, clear_queue, routing, delivered, RouterConversation
from ecs.utils.testcases import EcsTestCase

class MailTestCase(EcsTestCase):
    '''
    TestCase Class, modified to test whole mailsetup including mail sending and receiving
    overwrites settings.EMAIL_WHITELIST while running to empty because mail is not send, but stored in queue
    you probably want to "from lamson.server import SMTPError" inside your tests, to check for smtperrorcodes
    '''
    @classmethod
    def setUpClass(self):      
        # permit emails sent to all
        self.saved_EMAIL_WHITELIST= settings.EMAIL_WHITELIST
        settings.EMAIL_WHITELIST=[]
              
        #  import lamson ecsmail config, this makes the production frontend accessable from within the testcase
        import ecs.ecsmail.config
        self.mailclient = RouterConversation("somedude@notexisting.blu", "requests_tests")

    @classmethod
    def teardownClass(self):
        settings.EMAIL_WHITELIST=  self.saved_EMAIL_WHITELIST

    @classmethod
    def queue_clear(self):
        clear_queue(settings.LAMSON_TESTING_QUEUE)
        self.queue = Queue(settings.LAMSON_TESTING_QUEUE)
        
    def setUp(self):
        self.queue_clear()
        routing.Router.clear_states() 
        super(MailTestCase, self).setUp()

    def tearDown(self):
        super(MailTestCase, self).tearDown()
  
    @classmethod
    def queue_count(self):
        return self.queue.count()
    
    @classmethod
    def queue_list(self):
        return self.queue.keys()
    
    @classmethod
    def queue_get(self, key):
        return self.queue.get(key)
        
    @classmethod
    def deliver(self, To, From, Subject, Body):
        ''' Delivers the message trough ecsmail/lamson setup '''
        self.mailclient.deliver(To, From, Subject, Body)
        
    @classmethod
    def is_delivered(self, pattern):
        ''' returns message that matches the regex (searched = msgbody), or False if not found '''
        return delivered(pattern, self.queue)
