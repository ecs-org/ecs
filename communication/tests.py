from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from ecs.communication.models import Message, Thread
from ecs.utils.testcases import EcsTestCase
from ecs.core.models import Submission
from ecs.communication.models import Thread

class CommunicationTest(EcsTestCase):
    def setUp(self):
        for name in ('alice', 'bob', ):
            user = User(username=name)
            user.set_password('...')
            user.save()
            setattr(self, name, user)
    
        self.thread = Thread.objects.create(
            subject='test',
            sender=self.alice,
            receiver=self.bob,
            task=None,
            submission=None,
        )
        self.thread.add_message(self.alice, 'test')

        return super(CommunicationTest, self).setUp()
    
    def test_send_message(self):
        self.client.login(username='alice', password='...')

        response = self.client.get(reverse('ecs.communication.views.send_message'))
        self.failUnlessEqual(response.status_code, 200)
        
        message_count = Message.objects.count()
        response = self.client.post(reverse('ecs.communication.views.send_message'), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver': self.bob.pk,
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Message.objects.count(), message_count+1)
        message = Message.objects.all().order_by('-pk')[0]
        self.failUnlessEqual(message.sender, self.alice)
        self.failUnlessEqual(message.receiver, self.bob)
        
        response = self.client.get(reverse('ecs.communication.views.outbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message.thread in response.context['page'].object_list)
        response = self.client.get(reverse('ecs.communication.views.inbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message.thread in response.context['page'].object_list)

        self.client.logout()
        self.client.login(username='bob', password='...')

        response = self.client.get(reverse('ecs.communication.views.inbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message.thread in response.context['page'].object_list)

        response = self.client.get(reverse('ecs.communication.views.outbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message.thread in response.context['page'].object_list)

        self.client.logout()

    def test_send_message_invalid_submission(self):
        self.client.login(username='alice', password='...')
        try:
            non_existing_pk = Submission.objects.all().order_by('-pk')[0].pk+1
        except IndexError:
            non_existing_pk = 42
        response = self.client.post(reverse('ecs.communication.views.send_message', kwargs={'submission_pk': non_existing_pk}), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver': self.bob.pk,
        })
        self.failUnlessEqual(response.status_code, 404)

    def test_reply_message(self):
        thread = Thread.objects.create(subject='foo', sender=self.alice, receiver=self.bob)
        message = thread.add_message(self.alice, text="text")

        self.client.login(username='bob', password='...')
        response = self.client.post(reverse('ecs.communication.views.send_message', kwargs={'reply_to_pk': message.pk}), {
            'text': 'REPLY TEXT',
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.failUnlessEqual(message.receiver, self.alice)
        self.failUnlessEqual(message.sender, self.bob)

    def test_read_thread(self):
        self.client.login(username='alice', password='...')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(username='bob', password='...')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_bump_message(self):
        self.client.login(username='alice', password='...')
        response = self.client.get(reverse('ecs.communication.views.bump_message', kwargs={'message_pk': self.thread.last_message.pk}))
        self.failUnlessEqual(response.status_code, 200)

    def test_close_thread(self):
        self.client.login(username='alice', password='...')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(username='bob', password='...')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)

    def test_incoming_message_widget(self):
        self.client.login(username='alice', password='...')
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

    def test_outgoing_message_widget(self):
        self.client.login(username='alice', password='...')
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

        

