from django.test import TestCase
from django.http import HttpRequest, HttpResponse
from ecs.utils.middleware import SignedCookiesMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

class SignedCookiesTest(TestCase):
    def setUp(self):
        self.middleware = SignedCookiesMiddleware()
        self.auth_middleware = AuthenticationMiddleware()
        self.session_middleware = SessionMiddleware()
        
    def _process_request(self, request):
        self.session_middleware.process_request(request)
        self.auth_middleware.process_request(request)
        self.middleware.process_request(request)
        
    def _process_response(self, request, response):
        self.middleware.process_response(request, response)
        self.session_middleware.process_response(request, response)
        
    def test_middleware(self):
        request = HttpRequest()
        
        request.COOKIES['key'] = 'foo'
        self._process_request(request)
        self.failIf('key' in request.COOKIES)
        
        response = HttpResponse()
        request = HttpRequest()
        self._process_request(request)
        response.set_cookie('key', 'foo')
        self._process_response(request, response)
        signed_val = response.cookies['key'].value
        self.failIfEqual(signed_val, 'foo')
        
        request.COOKIES['key'] = signed_val
        self._process_request(request)
        self.failUnlessEqual(request.COOKIES['key'], 'foo')
        
