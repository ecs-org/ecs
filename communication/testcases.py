# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from ecs.ecsmail.testcases import MailTestCase
from ecs.communication.models import Message, Thread

from ecs.users.utils import get_user

class CommunicationTestCase(MailTestCase):
    '''
    Dereived from MailTestCase; Alice did create a new Communication.Thread with a test message "test subject", "test message"
    additions: self.alice, self.bob, self.thread, self.last_message 
    '''
    def setUp(self):
        super(CommunicationTestCase, self).setUp()
        self.alice = get_user('alice@example.com')
        self.bob = get_user('bob@example.com')
        self.thread = self.create_thread('test subject', 'test message', self.alice, self.bob)
        self.last_message = self.thread.last_message
        
    @classmethod    
    def create_thread(self, subject="", message="", sender=None, receiver=None, task=None, submission=None):
        '''
        sender and receiver must be django user objects and are defaulting to self.alice and self.bob
        '''
        if not sender: sender = self.alice
        if not receiver: receiver = self.bob      
        thread = Thread.objects.create(subject=subject, sender=sender, receiver=receiver, task=task, submission=submission)
        thread.add_message(sender, message)
        return thread
