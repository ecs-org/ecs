from uuid import uuid4

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from ecs.utils.testcases import LoginTestCase
from ecs.utils.pdfutils import wkhtml2pdf
from ecs.signature.views import sign


def _sign_dict():
    sign_dict = {
        'success_func': success_func,
        'parent_pk': None,
        'parent_type': None,    
        'document_uuid': uuid4().hex,
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
    return sign(request, _sign_dict(), force_mock=True, force_fail=False)

def sign_fail(request):
    return sign(request, _sign_dict(), force_mock=True, force_fail=True)

def success_func(request, document=None):
    return '/success/'


class SignatureTest(LoginTestCase):
    '''Tests for signature functions
    
    Tries to mock sign a document with simulating success, and failure
    '''
    
    def setUp(self, *args, **kwargs):
        rval = super(SignatureTest, self).setUp(*args, **kwargs)
        self.user = self.create_user('unittest-signing', profile_extra={'is_internal': True})
        self.user.groups.add(Group.objects.get(name='EC-Signing'))
        self.client.login(email='unittest-signing@example.com', password='password')
        
    def test_success(self):
        ''' Tests that signing a document is possible; Will use mock signing. '''
        response = self.client.get(reverse('ecs.signature.tests.sign_success'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/success/' in response['Location'])
    
    def test_failure(self):     
        ''' Tests that signing a document fails; Will use mock signing. '''
        response = self.client.get(reverse('ecs.signature.tests.sign_fail'))
        self.assertTrue(b'error' in response.content)
