from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ecs.messages.models import Message, Thread

class MessageTest(TestCase):
    def setUp(self):
        for name in ('alice', 'bob', ):
            user = User(username=name)
            user.set_password('...')
            user.save()
            setattr(self, name, user)
    
    def test_send_message(self):
        self.client.login(username='alice', password='...')

        response = self.client.get(reverse('ecs.messages.views.send_message'))
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.post(reverse('ecs.messages.views.send_message'), {
            'subject': 'SUBJECT',
            'text': 'TEXT',
            'receiver': self.bob.pk,
        })
        self.failUnlessEqual(response.status_code, 302)
        
        self.failUnlessEqual(Message.objects.count(), 1)
        message = Message.objects.get()
        self.failUnlessEqual(message.sender, self.alice)
        self.failUnlessEqual(message.receiver, self.bob)
        
        response = self.client.get(reverse('ecs.messages.views.outbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message in response.context['page'].object_list)
        response = self.client.get(reverse('ecs.messages.views.inbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message in response.context['page'].object_list)

        self.client.logout()
        self.client.login(username='bob', password='...')

        response = self.client.get(reverse('ecs.messages.views.inbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message in response.context['page'].object_list)

        response = self.client.get(reverse('ecs.messages.views.outbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message in response.context['page'].object_list)

        self.client.logout()

    def test_reply_message(self):
        thread = Thread.objects.create(subject='foo', sender=self.alice, receiver=self.bob)
        message = thread.add_message(self.alice, text="text")

        self.client.login(username='bob', password='...')
        response = self.client.post(reverse('ecs.messages.views.send_message', kwargs={'reply_to_pk': message.pk}), {
            'text': 'REPLY TEXT',
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.failUnlessEqual(message.receiver, self.alice)
        self.failUnlessEqual(message.sender, self.bob)

        
        
