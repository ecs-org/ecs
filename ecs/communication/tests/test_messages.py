from django.core.urlresolvers import reverse

from ecs.core.models import Submission
from ecs.communication.models import Message
from ecs.communication.testcases import CommunicationTestCase


class CommunicationTest(CommunicationTestCase):        
    ''' Tests for the ecs.communication modul, responsible for communication between users

    Thread creation, replying to messages, closing threads and genereal message/thread 
    accessibility and authorization is tested.
    '''

    def test_new_thread(self):
        '''Tests if a new thread can be created and is not accessible by another user not allowed to view it.
        Also checks that the message is only visible in the right widget.
        '''
        
        self.client.login(email='alice@example.com', password='password')

        response = self.client.get(reverse('ecs.communication.views.new_thread'))
        self.assertEqual(response.status_code, 200)
        
        message_count = Message.objects.count()
        response = self.client.post(reverse('ecs.communication.views.new_thread'), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver_type': 'person',
            'receiver_person': self.bob.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), message_count+1)
        message = Message.objects.all().order_by('-pk')[0]
        self.assertEqual(message.sender, self.alice)
        self.assertEqual(message.receiver, self.bob)
        
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(message.thread in response.context['page'].object_list)
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(message.thread in response.context['page'].object_list)

        self.client.logout()
        self.client.login(email='bob@example.com', password='password')

        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(message.thread in response.context['page'].object_list)

        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(message.thread in response.context['page'].object_list)

        self.client.logout()

    def test_new_thread_invalid_submission(self):
        '''Makes sure that a message referencing a nonexistent submission can't be created.
        '''
        
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
        self.assertEqual(response.status_code, 404)

    def test_reply_message(self):
        '''Tests if a personal message can be replied to.
        '''
        
        message = self.last_message
        self.client.login(email='bob@example.com', password='password')

        response = self.client.post(reverse('ecs.communication.views.read_thread',
            kwargs={'thread_pk': self.thread.pk}), {'text': 'REPLY TEXT'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.assertEqual(message.receiver, self.alice)
        self.assertEqual(message.sender, self.bob)

    def test_read_thread(self):
        '''Tests if a thread is really accessible for the users entitled to read it.
        '''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.assertEqual(response.status_code, 200)
        
        self.client.login(email='bob@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.assertEqual(response.status_code, 200)
        
    def test_bump_message(self):
        '''Tests if a thread can be bumped.'''
        
        message = self.last_message
        self.client.login(email='alice@example.com', password='password')

        response = self.client.post(reverse('ecs.communication.views.read_thread',
            kwargs={'thread_pk': self.thread.pk}), {'text': 'BUMP TEXT'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.assertEqual(message.sender, self.alice)
        self.assertEqual(message.receiver, self.bob)

    def test_close_thread(self):
        '''Makes sure that a thread can be closed.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.assertEqual(response.status_code, 302)
        
        self.client.login(email='bob@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.assertEqual(response.status_code, 302)

    def test_incoming_message_widget(self):
        '''Tests if the incoming message widget is accessible.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.assertEqual(response.status_code, 200)

    def test_outgoing_message_widget(self):
        '''Tests if the outgoing message widget is accessible.'''
        
        self.client.login(email='alice@example.com', password='password')
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.assertEqual(response.status_code, 200)

