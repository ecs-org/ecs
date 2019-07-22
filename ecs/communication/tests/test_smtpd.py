import shutil
import tempfile
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from django.conf import settings
from django.core.mail import make_msgid
from django.utils import timezone

from ecs.communication.testcases import CommunicationTestCase
from ecs.communication.smtpd import EcsMailReceiver


class SmtpdTest(CommunicationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpdir = tempfile.mkdtemp()
        TEST_SMTPD_CONFIG = {
            'listen_addr': ('127.0.0.1', 8024),
            'domain': 'ecs',
        }
        cls.OLD_SMTPD_CONFIG = settings.SMTPD_CONFIG
        cls.OLD_DOMAIN = settings.DOMAIN
        cls.OLD_DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
        settings.SMTPD_CONFIG = TEST_SMTPD_CONFIG
        settings.DOMAIN = "ecs"
        settings.DEFAULT_FROM_EMAIL = 'noreply@{}'.format(settings.DOMAIN)
        cls.mail_receiver = EcsMailReceiver()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)
        settings.SMTPD_CONFIG = cls.OLD_SMTPD_CONFIG
        settings.DOMAIN = cls.OLD_DOMAIN
        settings.DEFAULT_FROM_EMAIL = cls.OLD_DEFAULT_FROM_EMAIL
        super().tearDownClass()

    def process_message(self, recipients, msg):
        ret = self.mail_receiver.process_message(None, None, recipients,
            msg.as_bytes(unixfrom=True))
        code, description = ret.split(' ', 1)
        return int(code), description

    def test_data_size_limit(self):
        MB = 1024 * 1024
        self.assertEqual(EcsMailReceiver.MAX_MSGSIZE, MB)
        self.assertEqual(self.mail_receiver.data_size_limit, MB)

    def test_too_many_recipients(self):
        msg = MIMEText('')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>, Charlie <charlie@ecs>'

        code, description = self.process_message(['bob@ecs', 'charlie@ecs'], msg)
        self.assertEqual(code, 554)
        self.assertEqual(description, 'Too many recipients')

    def test_relay_denied(self):
        msg = MIMEText('This is a test mail.')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@someotherdomain>'

        code, description = self.process_message(['bob@someotherdomain'], msg)
        self.assertEqual(code, 550)
        self.assertEqual(description, 'Relay access denied')

    def test_invalid_message_format_emtpy(self):
        msg = MIMEText('')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>'

        code, description = self.process_message(['bob@ecs'], msg)
        self.assertEqual(code, 554)
        self.assertEqual(description, 'Invalid message format - empty message')

    def test_invalid_message_format_notext(self):
        msg = MIMEText('')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>'

        code, description = self.process_message(['bob@ecs'], msg)
        self.assertEqual(code, 554)
        self.assertEqual(description, 'Invalid message format - empty message')

    def test_invalid_message_format_image(self):
        msg = MIMEImage(b'P1\n1 1\n1')   # 1px PBM image
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>'

        code, description = self.process_message(['bob@ecs'], msg)
        self.assertEqual(code, 554)
        self.assertEqual(description, 'Invalid message format - invalid content type image/pbm')

    def test_invalid_message_format_attachment(self):
        msg = MIMEMultipart()
        msg.attach(MIMEText('This is a test mail.'))
        msg.attach(MIMEImage(b'P1\n1 1\n1'))
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>'

        code, description = self.process_message(['bob@ecs'], msg)
        self.assertEqual(code, 554)
        self.assertEqual(description, 'Invalid message format - invalid content type image/pbm')

    def test_invalid_recipient_no_hash(self):
        msg = MIMEText('This is a test mail.')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <bob@ecs>'

        code, description = self.process_message(['bob@ecs'], msg)
        self.assertEqual(code, 553)
        self.assertEqual(description, 'Invalid recipient <bob@ecs>')

    def test_invalid_recipient_invalid_hash(self):
        msg = MIMEText('This is a test mail.')
        msg['From'] = 'Alice <alice@example.com>'
        msg['To'] = 'Bob <ecs-b03838b0aad24f2ca5cfb54ff067dba6@ecs>'

        code, description = self.process_message(
            ['ecs-b03838b0aad24f2ca5cfb54ff067dba6@ecs'], msg)
        self.assertEqual(code, 553)
        self.assertEqual(description, 'Invalid recipient <ecs-b03838b0aad24f2ca5cfb54ff067dba6@ecs>')

    def test_plain(self):
        recipient = self.last_message.return_address
        msgid = make_msgid()
        msg = MIMEText('This is a test reply.')
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid

        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 250)
        self.assertEqual(description, 'Ok')
        self.assertEqual(self.thread.messages.count(), 2)

        reply = self.thread.messages.get(incoming_msgid=msgid)
        self.assertEqual(reply.text, 'This is a test reply.')
        self.assertEqual(reply.sender, self.bob)
        self.assertEqual(reply.receiver, self.alice)
        self.assertEqual(reply.creator, 'human')

    def test_html(self):
        recipient = self.last_message.return_address
        msgid = make_msgid()
        msg = MIMEText(
            '<html><body><p>This is a test reply.</p></body></html>', 'html')
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid

        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 250)
        self.assertEqual(description, 'Ok')
        self.assertEqual(self.thread.messages.count(), 2)

        reply = self.thread.messages.get(incoming_msgid=msgid)
        self.assertEqual(reply.text, 'This is a test reply.')
        self.assertEqual(reply.sender, self.bob)
        self.assertEqual(reply.receiver, self.alice)
        self.assertEqual(reply.creator, 'human')

    def test_mixed(self):
        recipient = self.last_message.return_address
        msgid = make_msgid()
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText('<html><body><p>HTML</p></body></html>', 'html'))
        msg.attach(MIMEText('PLAIN', 'plain'))
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid

        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 250)
        self.assertEqual(description, 'Ok')
        self.assertEqual(self.thread.messages.count(), 2)

        reply = self.thread.messages.get(incoming_msgid=msgid)

        # When both HTML and plain text is available, the latter takes
        # precedence.
        self.assertEqual(reply.text, 'PLAIN')
        self.assertEqual(reply.sender, self.bob)
        self.assertEqual(reply.receiver, self.alice)

    def test_answer_timeout_recipient(self):
        recipient = self.last_message.return_address
        self.last_message.timestamp = timezone.now() - timedelta(
            days=EcsMailReceiver.ANSWER_TIMEOUT + 1)
        self.last_message.save()

        msgid = make_msgid()
        msg = MIMEText('This is a test reply.')
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid

        self.assertEqual(EcsMailReceiver.ANSWER_TIMEOUT, 365)
        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 553)
        self.assertEqual(description, 'Invalid recipient <{}>'.format(recipient))

    def test_incoming_in_reply_to_and_auto_submitted(self):
        '''test that incoming emails have in_reply_to set.
            test that auto submitted emails have creator="auto-generated"
        '''
        recipient = self.last_message.return_address
        msgid = make_msgid()
        msg = MIMEText('This is a auto submitted test reply.')
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid
        msg['Auto-Submitted'] = 'auto-generated'

        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 250)
        self.assertEqual(description, 'Ok')
        self.assertEqual(self.thread.messages.count(), 2)

        reply = self.thread.messages.get(incoming_msgid=msgid)
        self.assertEqual(reply.text, 'This is a auto submitted test reply.')
        self.assertEqual(reply.sender, self.bob)
        self.assertEqual(reply.receiver, self.alice)
        self.assertEqual(reply.creator, 'auto-generated')
        self.assertEqual(reply.in_reply_to, self.last_message)

    def test_dont_forward_auto_submitted(self):
        '''test that auto generated messages are not forwarded'''
        recipient = self.last_message.return_address
        msgid = make_msgid()
        msg = MIMEText('This is a auto submitted test reply.')
        msg['From'] = 'Bob <alice@example.com>'
        msg['To'] = 'Alice <{}>'.format(recipient)
        msg['Message-ID'] = msgid
        msg['Auto-Submitted'] = 'auto-generated'

        code, description = self.process_message([recipient], msg)
        self.assertEqual(code, 250)
        self.assertEqual(description, 'Ok')
        self.assertEqual(self.thread.messages.count(), 2)

        reply = self.thread.messages.get(incoming_msgid=msgid)
        forwarded = reply.forward_smtp()
        self.assertFalse(forwarded)
