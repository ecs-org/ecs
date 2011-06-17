# -*- coding: utf-8 -*-
import os
import re

from django.core.urlresolvers import reverse

from ecs.utils.testcases import LoginTestCase
from ecs.documents.models import DocumentType
from ecs.notifications.models import NotificationType, Notification

from ecs.core.tests.submissions import create_submission_form

class NotificationFormTest(LoginTestCase):
    def test_creation_type_selection(self):
        NotificationType.objects.create(name='foo notif')
        response = self.client.get(reverse('ecs.notifications.views.select_notification_creation_type'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('foo notif' in response.content)
        
    def _create_POST_data(self, **extra):
        data = {
            'comments': 'foo comment',
        }
        data.update(extra)
        return data
        
    def test_notification_form(self):
        notification_type = NotificationType.objects.create(name='foo notif')

        # GET the form and expect a docstash transactions redirect, then follow this redirect
        response = self.client.get(reverse('ecs.notifications.views.create_notification', kwargs={'notification_type_pk': notification_type.pk}))
        self.failUnlessEqual(response.status_code, 302)
        url = response['Location']
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('foo notif' in response.content)
        self.failUnless('<form' in response.content)
        
        # POST the form in `autosave` mode
        response = self.client.post(url, self._create_POST_data(autosave='autosave'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf('<form' in response.content)

        # POST the form in `save` mode
        response = self.client.post(url, self._create_POST_data(save='save', comments='bar comment'))
        self.failUnlessEqual(response.status_code, 200)
        self.failIf('<form' in response.content)
        
        # POST the form in `submit` mode (incomplete data)
        response = self.client.post(url, self._create_POST_data(submit='submit'))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('<form' in response.content)
        form = response.context['form']
        self.failUnlessEqual(form['comments'].data, 'foo comment')
        
        # POST the form in `submit` mode (complete data) and follow the redirect
        submission_form = create_submission_form()
        response = self.client.post(url, self._create_POST_data(submit='submit', submission_forms=submission_form.pk))
        self.failUnlessEqual(response.status_code, 302)
        view_url = response['Location']
        response = self.client.get(view_url)
        obj = response.context['notification']
        self.failUnlessEqual(obj.comments, 'foo comment')
        self.failUnlessEqual(obj.submission_forms.all()[0], submission_form)

    def test_submission_data_for_notification(self):
        notification_type, _ = NotificationType.objects.get_or_create(name='foo notif')
        notification = Notification.objects.create(type=notification_type)
        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.notifications.views.submission_data_for_notification'), {'submission_form': submission_form.pk})
        self.failUnlessEqual(response.status_code, 200)

    def test_notification_pdf(self):
        notification_type, _ = NotificationType.objects.get_or_create(name='foo notif')
        notification = Notification.objects.create(type=notification_type)
        response = self.client.get(reverse('ecs.notifications.views.notification_pdf', kwargs={'notification_pk': notification.pk}))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless(response['Content-Type'], 'application/pdf')

    def _setup_POST_url(self):
        notification_type = NotificationType.objects.create(name='foo notif')
        response = self.client.get(reverse('ecs.notifications.views.create_notification', kwargs={'notification_type_pk': notification_type.pk}))
        return response['Location']
        
    def test_document_upload(self):
        url = self._setup_POST_url()
        upload_url = re.sub(r'new/\d+/', 'doc/upload/', url)    # XXX: ugly
        data = self._create_POST_data()
        doctype = DocumentType.objects.create(name='foo doctype')
        f = open(os.path.join(os.path.dirname(__file__), '..', 'core', 'tests', 'data', 'menschenrechtserklaerung.pdf'), 'rb')
        data.update({
            'document-file': f,
            'document-doctype': doctype.pk,
            'document-name': u'menschenrechtserklärung',
            'document-version': '3.1415',
            'document-date': '17.03.2010',
        })
        response = self.client.post(upload_url, data)
        f.close()
        self.failUnless('<form' in response.content)
        documents = response.context['documents']
        self.failUnlessEqual(len(documents), 1)
        doc = documents[0]
        self.failUnlessEqual(doc.version, '3.1415')
        self.failUnless(doc.file)
        
        response = self.client.get(reverse('ecs.documents.views.download_document', kwargs={'document_pk': doc.pk}))
        while response.status_code == 302:
            response = self.client.get(response['Location'])
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content[:4], '%PDF')
   
    def test_incomplete_upload(self):
        """ Regression test for the KeyError bug fixed in r729:b022598f8e55"""
        url = self._setup_POST_url()
        upload_url = re.sub(r'new/\d+/', 'doc/upload/', url)    # XXX: ugly
        data = self._create_POST_data()
        doctype = DocumentType.objects.create(name='regression doctype')
        data.update({
           'document-0-doctype': doctype.pk,
           'document-0-version': '3.1415',
           'document-0-date': '30.03.2010',
        })
        response = self.client.post(upload_url, data)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnless('<form' in response.content)

       

