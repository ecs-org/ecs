# -*- coding: utf-8 -*-
import os

from django.conf import settings

from ecs.communication.testcases import MailTestCase
from ecs.communication.mailutils import deliver


class MailutilsTest(MailTestCase):
    '''Outgoing mail tests for the ecsmail module
    
    Tests for sending mail in different forms and with or without attachments.
    '''

    def deliver(self, subject, message, from_email='alice@example.com',
        recipient_list='bob@example.com', message_html=None, attachments=None):

        return deliver(recipient_list, subject, message, from_email,
            message_html, attachments)

    def test_hello_world(self):
        '''Tests if an email can be sent from the system,
        '''
        
        self.deliver("some subject", "some body, first message")
        self.assertIn('first message', self.queue_get(0).get_payload())
    
    
    def test_text_and_html(self):
        '''Tests that creation and sending of html and text-only messages works.
        '''
        
        self.deliver("another subject", "second message", 
            message_html= "<html><head></head><body><b>this is bold</b></body>")
        
        msg = self.queue_get(0)
        mimetype, text_data = self.get_mimeparts(msg, "text", "plain")[0]
        mimetype, html_data = self.get_mimeparts(msg, "text", "html")[0]
        self.assertIn('second message', text_data)
        self.assertIn('this is bold', html_data)
    
    
    def test_attachments(self):
        '''Test for making sure that files can be attached to messages and
        that data attached is not altered.
        '''
        
        attachment_name = os.path.join(settings.PROJECT_DIR, "ecs", "core", "tests", "data", "menschenrechtserklaerung.pdf")
        attachment_data = open(attachment_name, "rb").read()
        
        # make two attachments, first attachment via a filename, second attachment via data supplied inline
        self.deliver("another subject", "this comes with attachments", 
            attachments=(("myname.pdf", attachment_data, "application/pdf"),))
   
        msg = self.queue_get(0)
        mimetype, text_data = self.get_mimeparts(msg, "text", "plain")[0]
        mimetype, pdf_data = self.get_mimeparts(msg, "application", "pdf")[0]
        self.assertIn('with attachments', text_data)
        self.assertEqual(attachment_data, pdf_data)


    def test_text_and_html_and_attachment(self):
        '''Makes sure that a message can consist of text and html and also has an attachment.
        Further checks that attached data is not altered during sending.
        '''
        
        attachment_name = os.path.join(settings.PROJECT_DIR, "ecs", "core", "tests", "data", "menschenrechtserklaerung.pdf")
        attachment_data = open(attachment_name, "rb").read()
        
        self.deliver("another subject", "another attachment", 
            message_html= "<html><head></head><body><b>bold attachment</b></body>", 
            attachments=(("myname.pdf", attachment_data, "application/pdf"),))
        
        msg = self.queue_get(0)
        mimetype, text_data = self.get_mimeparts(msg, "text", "plain")[0]
        mimetype, html_data = self.get_mimeparts(msg, "text", "html")[0]
        mimetype, pdf_data = self.get_mimeparts(msg, "application", "pdf")[0]
        
        self.assertIn('another attachment', text_data)
        self.assertIn('<b>bold attachment</b>', html_data)
        self.assertEqual(attachment_data, pdf_data)
