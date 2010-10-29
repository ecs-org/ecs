from nose.tools import assert_raises

from django.conf import settings
from django.contrib.auth.models import User

from lamson.server import SMTPError

from ecs.ecsmail.testcases import MailTestCase

class ecsmailTest(MailTestCase):
    def test_relay(self):
        ''' test relaying ''' 
        assert_raises(SMTPError, self.receive,
            "tooutside@someplace.org", "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
             "test", "test")

    def test_to_us_unknown(self):
        ''' mail to us, but unknown receipient address at our site '''
        assert_raises(SMTPError, self.receive,
            "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
            "nobody@notexisting.loc", "some text", "another text")

