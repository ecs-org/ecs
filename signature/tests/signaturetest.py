# -*- coding: utf-8 -*-
from uuid import uuid4
from nose.tools import ok_, eq_

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.http import urlquote

from ecs.utils.testcases import LoginTestCase
from ecs.utils.pdfutils import wkhtml2pdf
from ecs.documents.models import Document, DocumentType
from ecs.signature.views import sign
 
SIGN_INDICATE_SUCCCES = 'about:sucess'
SIGN_INDICATE_FAILURE = 'about:error'


def _sign_dict():
    sign_dict = {
        'success_func': 'ecs.signature.tests.signaturetest.success_func',
        'error_func': 'ecs.signature.tests.signaturetest.error_func',
        'parent_pk': None,
        'parent_type': None,    
        'document_uuid': uuid4().get_hex(),
        'document_name': 'Unit-Test',
        'document_type': 'other',
        'document_version': '1',
        'document_filename': 'unittest.pdf',
        'document_barcodestamp': True,
        'html_preview': '<HTML><BODY>unittest</BODY></HTML>',
        }
        
    sign_dict['pdf_data'] = wkhtml2pdf(sign_dict['html_preview'])
    return sign_dict

def sign_success(request):
    return sign(request, _sign_dict(), always_mock= True, always_fail= False)

def sign_fail(request):
    return sign(request, _sign_dict(), always_mock= True, always_fail= True)

def success_func(document_pk=None):
    document = get_object_or_404(Document, pk=document_pk) 
    return (SIGN_INDICATE_SUCCCES)
    
def error_func(parent_pk=None, description=''):
    return (SIGN_INDICATE_FAILURE+"&"+ urlquote(description))


class SignatureTest(LoginTestCase):
    '''Tests for signature functions
    
    Tries to mock sign a document with simulating success, and failure
    '''
    
    def setUp(self, *args, **kwargs):
        rval = super(SignatureTest, self).setUp(*args, **kwargs)
        self.user = self.create_user('unittest-signing', profile_extra={'is_internal': True})
        self.user.groups.add(Group.objects.get(name=u'EC-Signing Group'))    
        self.client.login(email='unittest-signing@example.com', password='password')
        
    def test_success(self):
        '''Tests that signing a document is possible; Will use mock signing.
        '''
        response = self.client.get(reverse('ecs.signature.tests.signaturetest.sign_success'))
        redirecturl = response['Location']
        print redirecturl
        eq_ (redirecturl, SIGN_INDICATE_SUCCCES)
    
    def test_failure(self):     
        '''Tests that signing a document fails; Will use mock signing.
        '''
        response = self.client.get(reverse('ecs.signature.tests.signaturetest.sign_fail'))
        redirecturl = response['Location']
        print redirecturl
        eq_ (redirecturl[:len(SIGN_INDICATE_FAILURE)], SIGN_INDICATE_FAILURE)

