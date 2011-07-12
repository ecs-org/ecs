# -*- coding: utf-8 -*-

from nose.tools import ok_, eq_
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.core.models import Submission
from ecs.communication.models import Message, Thread
from ecs.communication.testcases import CommunicationTestCase


class CommunicationTest(CommunicationTestCase):        
    '''Class for testing the communication facilities of the system'''
    
    
    """
    def test_from_ecs_to_outside_and_back_to_us(self):
        ''' 
        standard test setup makes a new ecs internal message (which currently will send an email to the user)
        and then answer to that email which is then forwarded back to the original sender
        '''
        eq_(self.queue_count(), 1)
        ok_(self.is_delivered("test message"))
        
        self.receive("testsubject", "second message", self.bob.email,  
            "".join(("ecs-", self.last_message.uuid, "@", settings.ECSMAIL ['authoritative_domain'])),
            )
        eq_(self.queue_count(), 2)
        ok_(self.is_delivered("second message"))
    """

        
    def test_new_thread(self):
        '''Tests if a new thread can be created and is accessible by another user.
        Also checks that the message is only visible in the right widget.'''
        
        self.client.login(email='alice@example.com', password='password')

        response = self.client.get(reverse('ecs.communication.views.new_thread'))
        self.failUnlessEqual(response.status_code, 200)
        
        message_count = Message.objects.count()
        response = self.client.post(reverse('ecs.communication.views.new_thread'), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver_type': 'person',
            'receiver_person': self.bob.pk,
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Message.objects.count(), message_count+1)
        message = Message.objects.all().order_by('-pk')[0]
        self.failUnlessEqual(message.sender, self.alice)
        self.failUnlessEqual(message.receiver, self.bob)
        
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message.thread in response.context['page'].object_list)
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message.thread in response.context['page'].object_list)

        self.client.logout()
        self.client.login(email='bob@example.com', password='password')

        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message.thread in response.context['page'].object_list)

        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message.thread in response.context['page'].object_list)

        self.client.logout()

    def test_new_thread_invalid_submission(self):
        '''Makes sure that a message referencing a nonexistent submission can't be created.'''
        
        self.client.login(email='alice@example.com', password='password')
        try:
            non_existing_pk = Submission.objects.all().order_by('-pk')[0].pk+1
        except IndexError:
            non_existing_pk = 42
        response = self.client.post(reverse('ecs.communication.views.new_thread', kwargs={'submission_pk': non_existing_pk}), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver': self.bob.pk,
        })
        self.failUnlessEqual(response.status_code, 404)

    def test_reply_message(self):
        '''Tests that a personal message can be replied to.'''
        
        message = self.last_message
        self.client.login(email='bob@example.com', password='password')

        response = self.client.post(reverse('ecs.communication.views.read_thread',
            kwargs={'thread_pk': self.thread.pk}), {'text': 'REPLY TEXT'})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.failUnlessEqual(message.receiver, self.alice)
        self.failUnlessEqual(message.sender, self.bob)

    def test_read_thread(self):
        '''Tests that a thread can be read by both users entitled to read it.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(email='bob@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_bump_message(self):
        '''Tests if a thread can be bumped.'''
        
        message = self.last_message
        self.client.login(email='alice@example.com', password='password')

        response = self.client.post(reverse('ecs.communication.views.read_thread',
            kwargs={'thread_pk': self.thread.pk}), {'text': 'BUMP TEXT'})
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.failUnlessEqual(message.sender, self.alice)
        self.failUnlessEqual(message.receiver, self.bob)

    def test_close_thread(self):
        '''Makes sure that a thread can be closed.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 302)
        
        self.client.login(email='bob@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 302)

    def test_incoming_message_widget(self):
        '''Tests that the incoming message widget is accessible.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

    def test_outgoing_message_widget(self):
        '''Tests that the outgoing message widget is accessible.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

