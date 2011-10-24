# -*- coding: utf-8 -*-
import os
import re
import datetime

from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType

from ecs.utils.testcases import LoginTestCase
from ecs.documents.models import DocumentType
from ecs.notifications.models import NotificationType, Notification, ProgressReportNotification
from ecs.core.models import Vote
from ecs.core.tests.submissions import create_submission_form

class NotificationFormTest(LoginTestCase):
    '''Tests for the Notification and NotificationType module
    
    Tests for creating Notifications, upload of Notification documents, PDF document generation and Notification type selection.
    '''
    
    def test_creation_type_selection(self):
        '''Tests if a notification type can be created and if the view for its selection is accessible.
        '''
        
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
        '''Tests notification creation and autosave mode. Further tests if notification can be saved,
        submited with incomplete data and finally if the correct redirect happens if submitted with complete data.
        '''
        
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
        '''Tests if the submission_data_for_notification view is accessible for a created notification for a submission.
        '''
        
        notification_type, _ = NotificationType.objects.get_or_create(name='foo notif')
        notification = Notification.objects.create(type=notification_type)
        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.notifications.views.submission_data_for_notification'), {'submission_form': submission_form.pk})
        self.failUnlessEqual(response.status_code, 200)

    def test_notification_pdf(self):
        '''Tests if a pdf is produced if a Notification is created.
        '''
        
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
        '''Tests if a pdf file can be uploaded. Further tests if meta data of the document is stored correctly and
        if the resuting download link contains a PDF file.
        '''
        
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
        '''Tests an incomplete document upload. Regression test for the KeyError bug fixed in r729:b022598f8e55
        '''
        
        
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

    def test_vote_extension_workflow(self):
        from ecs.core.tests.submissions import create_submission_form
        from django.contrib.auth.models import Group
        
        call_command('bootstrap')
        
        now = datetime.datetime.now()
        nt = NotificationType.objects.get(form='ecs.core.forms.ProgressReportNotificationForm')

        presenter = self.create_user('test_presenter')
        office = self.create_user('test_office', profile_extra={'is_internal': True})
        office.groups.add(Group.objects.get(name=u'EC-Office'))
        executive = self.create_user('text_executive', profile_extra={'is_internal': True, 'is_executive_board_member': True})
        executive.groups.add(
            Group.objects.get(name=u'EC-Executive Board Group'),
            Group.objects.get(name=u'EC-Notification Review Group'),
        )

        sf = create_submission_form(presenter=presenter)

        with self.login('test_presenter'):
            response = self.client.get(reverse('ecs.notifications.views.create_notification', kwargs={'notification_type_pk': nt.pk}))
            url = response['Location'] # docstash redirect

            # no vote yet => we cannot select the submission form
            response = self.client.get(url)
            self.assertFalse(response.context['form'].fields['submission_form'].queryset.filter(pk=sf.pk).exists())
        
            # create a permanent final postive vote
            vote = sf.votes.create(result='1', is_final=True, signed_at=now, published_at=now, valid_until=now.replace(year=now.year + 1))
        
            # now we have a vote => submission form is selectable
            response = self.client.get(url)
            self.assertTrue(response.context['form'].fields['submission_form'].queryset.filter(pk=sf.pk).exists())
            
            # create a notification, request a vote extension
            response = self.client.post(url, {
                'submission_form': sf.pk,
                'extension_of_vote_requested': 'on',
                'runs_till': '12.12.2012',
                'submit': 'on',
                'SAE_count': '0',
                'SUSAR_count': '0',
                'study_started': 'on',
            })
            self.assertEqual(response.status_code, 302)
            notification = self.client.get(response['Location']).context['notification']
        
        def do_review(user):
            response = self.client.get(reverse('ecs.tasks.views.my_tasks', kwargs={'submission_pk': sf.submission.pk}))
            task = response.context['open_tasks'].get(
                data_id=notification.pk, 
                content_type=ContentType.objects.get_for_model(ProgressReportNotification),
            )
            task.accept(user)
            response = self.client.get(task.url)
            self.assertEqual(response.status_code, 200)
            
            response = self.client.post(task.url, {
                'task_management-submit': 'Abschicken',
                'task_management-action': 'complete_0',
                'task_management-post_data': 'text=Test.',
            })
            self.assertEqual(response.status_code, 302)

        # office review
        with self.login('test_office'):
            do_review(office)
        
        # executive review
        with self.login('text_executive'):
            do_review(executive)
        
        notification = ProgressReportNotification.objects.get(pk=notification.pk)
        old_valid_until = vote.valid_until
        vote = Vote.objects.get(pk=vote.pk)
        self.assertEqual(vote.valid_until, old_valid_until.replace(year=old_valid_until.year + 1))
        
        
        
