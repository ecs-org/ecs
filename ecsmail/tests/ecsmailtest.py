# -*- coding: utf-8 -*-

import re
from nose.tools import assert_raises, ok_, eq_
from django.conf import settings
from lamson.server import SMTPError

from ecs.ecsmail.testcases import MailTestCase

class ecsmailIncomingTest(MailTestCase):
    def test_relay(self):
        ''' test relaying ''' 
        assert_raises(SMTPError, self.receive,
            "some subject", "some body",
            "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
            "tooutside@someplace.org")

    def test_to_us_unknown(self):
        ''' mail to us, but unknown receipient address at our site '''
        assert_raises(SMTPError, self.receive,
            "some subject", "some body",
            "nobody@notexisting.loc",
            "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
             )

class ecsmailOutgoingTest(MailTestCase):
    def test_hello_world(self):
        self.deliver("some subject", "some body, first message", "noreply@example.org", "target@example.org")
        eq_(self.queue_count(), 1)
        ok_(self.is_delivered("first message"))
    
    def test_text_and_html(self):
        self.deliver("another subject", "second message", "noreply@example.org", "target@example.org", 
            "<b> this is bold</b>")
        x = self.is_delivered("second message")
        ok_(x)
        ok_(re.search("this is bold", x))

        
