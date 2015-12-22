from email.iterators import typed_subpart_iterator

from django.core import mail

from ecs.utils.testcases import EcsTestCase
from ecs.communication.models import Thread
from ecs.users.utils import get_user


class MailTestCase(EcsTestCase):
    '''TestCase Class, for testing Mail inside the ecs environment'''

    def setUp(self):
        mail.outbox = []
        super(MailTestCase, self).setUp()

    @staticmethod
    def get_mimeparts(msg, maintype="*", subtype="*"):
        ''' Takes a email.Message Object and returns a list of matching maintype, subtype message parts as list [[mimetype, rawdata]*] '''
        l = []
        for part in typed_subpart_iterator(msg, maintype, subtype):
            l.append([part.get_content_type(), part.get_payload(decode=True)])
        return l

    def queue_get(self, idx):
        return getattr(mail, 'outbox', [])[idx].message()


class CommunicationTestCase(MailTestCase):
    '''
    Dereived from MailTestCase; Alice did create a new Communication.Thread with a test message "test subject", "test message"
    additions: self.alice, self.bob, self.thread, self.last_message
    '''
    def setUp(self):
        super(CommunicationTestCase, self).setUp()
        self.alice = get_user('alice@example.com')
        self.bob = get_user('bob@example.com')

        self.thread = Thread.objects.create(subject='test subject',
            sender=self.alice, receiver=self.bob)
        self.last_message = self.thread.add_message(
            self.thread.sender, 'test message')
