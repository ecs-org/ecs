# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User

from lamson.testing import Queue, clear_queue, routing, delivered, RouterConversation

from ecs.utils.testcases import EcsTestCase
from ecs.communication.models import Message, Thread


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
        import ecs.ecsmail.config.boot
        self.mailclient = RouterConversation("somedude@notexisting.blu", "requests_tests")

        #from ecs.utils.raise_thread import ThreadWithExc
        #import asyncore 
        #logloader = lambda: utils.make_fake_settings('127.0.0.1', settings.RELAY_CONFIG['port']) 
        #sys.path.append(os.getcwd()) 
        #self.logserver = logloader()
        #self.logserver.receiver.start()
        #logging.info("SMTPReceiver started on %s:%d." % ('127.0.0.1', settings.RELAY_CONFIG['port']))
        #self.logserver.poller = ThreadWithExc(target=asyncore.loop, kwargs={'timeout':0.1, 'use_poll':True})
        #self.logserver.poller.start() 
        #print (self.logserver.poller)
       
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

class MessageTestCase(MailTestCase):
    '''
    Dereived from MailTestCase, additionaly setup two ecs users, fromuser and touser, and adds functions to add internal ecs -messages
    '''
    def setUp(self):
        super(MessageTestCase, self).setUp()
        
        self.fromuser = User(username='fromuser')
        self.fromuser.email = "notexisting@fromuser.notexisting.notexisting"
        self.fromuser.set_password('password')
        self.fromuser.save()
        self.touser = User(username='touser')
        self.touser.email = "notexisting@touser.nirvana.nirvana"
        self.touser.set_password('password')
        self.touser.save()

    @classmethod    
    def create_thread(self, To=None, From=None, Subject="", Task=None, Submission=None):
        '''
        Creates a new ecs-message thread, To and From must be django.contrib.user objects, 
        and are defaulting to self.touser self.fromuser
        Task, Submission the ecs/core/models; Returns thread model
        '''
        if not To:  To = self.touser
        if not From: From = self.fromuser      
        thread = Thread.objects.create(subject=Subject, sender=From, receiver=To, task=Task, submission=Submission)
        return thread
     
    @classmethod
    def msg_to_thread(self, thread, To=None, Body=""):
        '''
        Adds a message to a thread; To: can be either From or To User from create_thread
        and is defaulting to touser
        creates a email to To, with thread subject and body
        returns the created message model object
        '''
        # FIXME: think what and how it should happen that another person answers to a thread (realistic szenario, through forwards)
        if not To:  To = self.touser
        message = thread.add_message(To, text=Body)
        return message
        
    def is_in_thread(self, thread, pattern):
        '''
        returns message that is stored inside thread that matches the pattern, or None if not found
        '''
        raise(NotImplementedError)
                