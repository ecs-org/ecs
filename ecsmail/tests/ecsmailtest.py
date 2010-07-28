from nose.tools import *
from ecs.ecsmail.testcases import MailTestCase, MessageTestCase
from lamson.server import SMTPError
from django.conf import settings
from django.contrib.auth.models import User
from ecs.messages.models import Message, Thread

class ecsmailTest(MailTestCase):
    def test_relay(self):
        ''' test relaying ''' 
        assert_raises(SMTPError, self.deliver,
            "tooutside@someplace.org", "".join(("ecs-123@", settings.FROM_DOMAIN)), "test", "test")

    def test_to_us_unknown(self):
        ''' mail to us, but unknown receipient address at our site '''
        assert_raises(SMTPError, self.deliver,
            "".join(("ecs-123@",settings.FROM_DOMAIN)), "nobody@notexisting.loc", "some text", "another text")

class simpleMessagesTest(MessageTestCase):
    def test_from_ecs_to_outside_and_back_to_us(self):
        ''' 
        this makes a new ecs internal message (which currently will send an email to the user)
        and then answer to that email which is then forwared back to the original sender
        '''
        thread= self.create_thread(To=self.touser, From=self.fromuser, Subject="blu", Task=None, Submission=None)
        message = self.msg_to_thread(thread, To= self.fromuser, Body= "first message")
        eq_(self.queue_count(), 1)
        ok_(self.is_delivered("first message"))
        
        self.queue_clear()
        self.deliver("".join(("ecs-", message.uuid, "@", settings.FROM_DOMAIN)),
            "fromoutside@someplace.org", "testsubject", "second message")
        eq_(self.queue_count(), 1)
        # FIXME: this is naive, because it just tests if ecsmail is sending the routed message back to the receipient, but doesnt check thread values
        