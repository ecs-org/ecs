from nose.tools import *
from django.test import TestCase
from django.conf import settings

from django.contrib.auth.models import User
from ecs.messages.models import Message, Thread

from lamson import utils
from lamson import server, routing
from lamson.server import SMTPError
# FIXME: this should override lamsons default "run/queue" settings but it doesnt, so we set settings.TESTING_QUEUE to run/queue
from lamson import testing
testing.TEST_QUEUE = settings.TESTING_QUEUE
from lamson.testing import *
testing.TEST_QUEUE = settings.TESTING_QUEUE

# tryouts to get rid of logging server for testing
#testloader = lambda: utils.make_fake_settings('127.0.0.1', settings.ECSMAIL_LOGSERVER_PORT) 
#testlamson = testloader()
#testlamson.receiver.start()
# other try: testlamson = utils.make_fake_settings('127.0.0.1', settings.ECSMAIL_LOGSERVER_PORT)

#  import lamson ecsmail config, this somehow starts lamson ecsmail server (or makes it accessable)
import ecs.ecsmail.config.boot

class MailTest(TestCase):
    def setUp(self):
        self.client = RouterConversation("somedude@notexisting.blu", "requests_tests")
        clear_queue(settings.TESTING_QUEUE)
        routing.Router.clear_states() 
        
        self.fromuser = User(username='fromuser')
        self.fromuser.email = "notexisting@notexisting.notexisting"
        self.fromuser.set_password('password')
        self.fromuser.save()

        self.touser = User(username='touser')
        self.touser.email = "nirvana@nirvana.nirvana"
        self.touser.set_password('password')
        self.touser.save()

    def test_relay(self):
        ''' test relaying ''' 
        assert_raises(SMTPError, self.client.deliver,
            "tooutside@someplace.org", "".join(("ecs-123@", settings.FROM_DOMAIN)), "test", "test")

    def test_to_us_unknown(self):
        ''' mail to us, but unknown receipient address at our site '''
        assert_raises(SMTPError, self.client.say,
            "".join(("ecs-123@",settings.FROM_DOMAIN)), "some text")

    def test_from_ecs_to_outside_and_back_to_us(self):
        ''' this makes a new ecs internal message (which currently will send an email to the user, and then answer to that email '''
        thread = Thread.objects.create(subject="test mail subject",
            sender=self.fromuser, receiver=self.touser, task=None, submission=None,
        )
        message = thread.add_message(self.fromuser, text="test mail message")
        eq_(queue(settings.TESTING_QUEUE).count(), 1)
        ok_(delivered("test mail message", queue(settings.TESTING_QUEUE)))

        clear_queue(settings.TESTING_QUEUE)
        self.client.deliver("".join(("ecs-", message.uuid, "@", settings.FROM_DOMAIN)),
            "fromoutside@someplace.org", "testsubject", "testmessage")
        eq_(queue(settings.TESTING_QUEUE).count(), 1)
