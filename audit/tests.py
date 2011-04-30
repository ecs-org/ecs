# -*- coding: utf-8 -*-
import time

from django.conf import settings
from django.core.urlresolvers import reverse

from ecs.utils.testcases import EcsTestCase
from ecs.audit.models import AuditTrail
from ecs.users.utils import create_user


class BasicTests(EcsTestCase):
    def test_settings(self):
        self.failUnless(hasattr(settings, 'ENABLE_AUDIT_TRAIL'))
        self.failUnless(hasattr(settings, 'AUDIT_TRAIL_IGNORED_MODELS'))
           
    def test_create_user(self):
        audit_trail_entries_count = AuditTrail.objects.count()
        create_user('audit_trail_test_user@example.com')  # there are being created some objects (User,UserProfile,UserSettings)
        self.assertNotEqual(audit_trail_entries_count, AuditTrail.objects.count())
    
    def test_line_formatting(self):
        a = AuditTrail.objects.all()[0]
        a.get_log_line()

    def test_unicode(self):
        a = AuditTrail.objects.all()[0]
        unicode(a)

class ViewTests(EcsTestCase):
    def setUp(self, *args, **kwargs):
        inspector = create_user('inspector@example.com')
        inspector.set_password('4223')
        inspector.save()
        iprofile = inspector.get_profile()
        iprofile.executive_board_member = True
        iprofile.save()

        unauthorized_user = create_user('unauthorized@example.com')
        unauthorized_user.set_password('4223')
        unauthorized_user.save()

        return super(ViewTests, self).setUp(*args, **kwargs)

    def test_log_view_txt(self):
        self.client.login(email='inspector@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', args=('txt',)))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Type'], 'text/plain')

    def test_log_view_html(self):
        self.client.login(email='inspector@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', args=('html',)))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Type'], 'text/html')

    def test_log_view_txt_unauthorized(self):
        self.client.login(email='unauthorized@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', args=('txt',)))
        self.failUnlessEqual(response.status_code, 302) # redirect to login page

    def test_log_view_html_unauthorized(self):
        self.client.login(email='unauthorized@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', args=('html',)))
        self.failUnlessEqual(response.status_code, 302)  # redirect to login page

    def test_log_view_foo(self):
        self.client.login(email='inspector@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', args=('foo',)))
        self.failUnlessEqual(response.status_code, 404)  # foo is not a valid log format

    def test_paging(self):
        for i in xrange(100): # create a lot of audit trail entries
            create_user('audittrailpagingtest{0}@example.com'.format(i))

        first_entry = AuditTrail.objects.all().order_by('pk')[0]
        last_entry = AuditTrail.objects.all().order_by('-pk')[0]

        self.client.login(email='inspector@example.com', password='4223')
        response = self.client.get(reverse('ecs.audit.views.log', kwargs={'format': 'html', 'limit': '50', 'since': str(first_entry.pk)}))
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.get(reverse('ecs.audit.views.log', kwargs={'format': 'html', 'limit': '50', 'until': str(last_entry.pk)}))
        self.failUnlessEqual(response.status_code, 200)

