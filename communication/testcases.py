# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User

from ecs.ecsmail.testcases import MailTestCase
from ecs.communication.models import Message, Thread



class CommunicationTestCase(MailTestCase):
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
                