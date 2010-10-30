# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from ecs.ecsmail.testcases import MailTestCase
from ecs.communication.models import Message, Thread


class CommunicationTestCase(MailTestCase):
    '''
    Dereived from MailTestCase; additions: self.alice, self.bob, self.thread, alice did send test message
    '''
    def setUp(self):
        super(CommunicationTestCase, self).setUp()
        self.alice = User.objects.get(username='alice')
        self.bob = User.objects.get(username='bob')
        self.thread = self.create_thread('test subject', 'test message', self.alice, self.bob)
        
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
