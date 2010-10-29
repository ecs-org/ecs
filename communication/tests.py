from nose.tools import ok_, eq_
from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.core.models import Submission
from ecs.communication.models import Message, Thread
from ecs.communication.testcases import CommunicationTestCase


class CommunicationTest(CommunicationTestCase):        
    
    def test_from_ecs_to_outside_and_back_to_us(self):
        ''' 
        this makes a new ecs internal message (which currently will send an email to the user)
        and then answer to that email which is then forwared back to the original sender
        '''
        import logging
        logger = logging.getLogger()
        logger.info("list: %s" % str(self.queue_list()))
        thread= self.create_thread("testsubject", "first message", self.alice, self.bob)
        logger.info("list: %s" % str(self.queue_list()))
        eq_(self.queue_count(), 1)
        ok_(self.is_delivered("first message"))
        
        
        self.queue_clear()
        self.receive("".join(("ecs-", message.uuid, "@", settings.ECSMAIL ['authoritative_domain'])),
            "fromoutside@someplace.org", "testsubject", "second message")
        eq_(self.queue_count(), 1)
        # FIXME: this is naive, because it just tests if ecsmail is sending, but doesnt further


    def test_send_message(self):
        self.client.login(username='alice', password='password')

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
        self.client.login(username='bob', password='password')

        response = self.client.get(reverse('ecs.communication.views.inbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(message.thread in response.context['page'].object_list)

        response = self.client.get(reverse('ecs.communication.views.outbox'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf(message.thread in response.context['page'].object_list)

        self.client.logout()

    def test_send_message_invalid_submission(self):
        self.client.login(username='alice', password='password')
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

        self.client.login(username='bob', password='password')
        response = self.client.post(reverse('ecs.communication.views.send_message', kwargs={'reply_to_pk': message.pk}), {
            'text': 'REPLY TEXT',
        })
        self.failUnlessEqual(response.status_code, 302)
        self.failUnlessEqual(Message.objects.count(), 2)
        message = Message.objects.exclude(pk=message.pk).get()
        self.failUnlessEqual(message.receiver, self.alice)
        self.failUnlessEqual(message.sender, self.bob)

    def test_read_thread(self):
        self.client.login(username='alice', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_bump_message(self):
        self.client.login(username='alice', password='password')
        response = self.client.get(reverse('ecs.communication.views.bump_message', kwargs={'message_pk': self.thread.last_message.pk}))
        self.failUnlessEqual(response.status_code, 200)

    def test_close_thread(self):
        self.client.login(username='alice', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse('ecs.communication.views.close_thread', kwargs={'thread_pk': self.thread.pk}))
        self.failUnlessEqual(response.status_code, 200)

    def test_incoming_message_widget(self):
        self.client.login(username='alice', password='password')
        response = self.client.get(reverse('ecs.communication.views.incoming_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

    def test_outgoing_message_widget(self):
        self.client.login(username='alice', password='password')
        response = self.client.get(reverse('ecs.communication.views.outgoing_message_widget'))
        self.failUnlessEqual(response.status_code, 200)

        

