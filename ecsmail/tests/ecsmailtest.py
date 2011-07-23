# -*- coding: utf-8 -*-

import os
import re
from nose.tools import assert_raises, ok_, eq_
from django.conf import settings
from lamson.server import SMTPError

from ecs.ecsmail.testcases import MailTestCase

class ecsmailIncomingTest(MailTestCase):
    '''Incoming mail tests for the ecsmail module
    
    Tests for relaying and receiving incoming mail messages.
    '''
    
    def test_relay(self):
        '''Makes sure that the ecsmail module does not act as an open mail relay'''
         
        assert_raises(SMTPError, self.receive,
            "some subject", "some body",
            "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
            "tooutside@someplace.org")


    def test_to_us_unknown(self):
        '''Makes sure that mail to an unknown recipient is rejected.
        '''
        
        assert_raises(SMTPError, self.receive,
            "some subject", "some body",
            "from.nobody@notexisting.loc",
            "".join(("ecs-123@", settings.ECSMAIL ['authoritative_domain'])),
             )


class ecsmailOutgoingTest(MailTestCase):
    '''Outgoing mail tests for the ecsmail module
    
    Tests for sending mail in different forms and with or without attachments.
    '''
    
    def test_hello_world(self):
        '''Tests if an email can be sent from the system,
        '''
        
        self.deliver("some subject", "some body, first message")
        eq_(self.queue_count(), 1)
        ok_(self.is_delivered("first message"))
    
    
    def test_text_and_html(self):
        '''Tests that creation and sending of html and text-only messages works.
        '''
        
        self.deliver("another subject", "second message", 
            message_html= "<html><head></head><body><b>this is bold</b></body>")
        x = self.is_delivered("second message")
        ok_(x)
        
        msg = self.convert_raw2message(x)
        mimetype, html_data = self.get_mimeparts(msg, "text", "html") [0]
        ok_(re.search("this is bold", html_data))
    
    
    def test_attachments(self):
        '''Test for making sure that files can be attached to messages and
        that data attached is not altered.
        '''
        
        attachment_name = os.path.join(settings.PROJECT_DIR, "core", "tests", "data", "menschenrechtserklaerung.pdf")
        attachment_data = open(attachment_name, "rb").read()
        
        # make two attachments, first attachment via a filename, second attachment via data supplied inline
        self.deliver("another subject", "this comes with attachments", 
            attachments=[attachment_name, ["myname.pdf", attachment_data, "application/pdf"]])
        x = self.is_delivered("with attachments")
        ok_(x)
   
        msg = self.convert_raw2message(x)
        mimetype, pdf_data = self.get_mimeparts(msg, "application", "pdf") [0]
        eq_(attachment_data, pdf_data)
        mimetype, pdf_data = self.get_mimeparts(msg, "application", "pdf") [1]
        eq_(attachment_data, pdf_data)
        
        
    def test_text_and_html_and_attachment(self):
        '''Makes sure that a message can consist of text and html and also has an attachment.
        Further checks that attached data is not altered during sending.
        '''
        
        attachment_name = os.path.join(settings.PROJECT_DIR, "core", "tests", "data", "menschenrechtserklaerung.pdf")
        attachment_data = open(attachment_name, "rb").read()
        
        self.deliver("another subject", "another attachment", 
            message_html= "<html><head></head><body><b>bold attachment</b></body>", 
            attachments=[attachment_name])
        x = self.is_delivered("another attachment")
        ok_(x)
        
        msg = self.convert_raw2message(x)
        mimetype, html_data = self.get_mimeparts(msg, "text", "html") [0]
        mimetype, pdf_data = self.get_mimeparts(msg, "application", "pdf") [0]
        
        ok_(re.search("<b>bold attachment</b>", html_data))
        eq_(attachment_data, pdf_data)
        