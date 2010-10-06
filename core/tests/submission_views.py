from django.core.urlresolvers import reverse
from ecs.utils.testcases import LoginTestCase
from ecs.core.tests.submissions import create_submission_form

class SubmissionViewsTestCase(LoginTestCase):
    def test_create_submission_form(self):
        url = reverse('ecs.core.views.create_submission_form')
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 302)
        url = response['Location']
        
        # post some data
        response = self.client.post(url, {})
        self.failUnlessEqual(response.status_code, 200)
        
        # from docstash
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
    def test_readonly_submission_form(self):
        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_submission_pdf(self):
        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.core.views.submission_pdf', kwargs={'submission_form_pk': submission_form.pk}))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response['Content-Type'], 'application/pdf')
        self.failUnlessEqual(response.content[:4], '%PDF')
        
    def test_submission_form_search(self):
        create_submission_form('X2020/1')
        create_submission_form('2020/0042')
        create_submission_form('2020/9942')
        url = reverse('ecs.core.views.submission_form_list')
        
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['unscheduled_submissions']), 3)
        
        response = self.client.post(url, {'keyword': '42'})
        self.failUnless(response.status_code, 200)
        self.failUnlessEqual(len(response.context['unscheduled_submissions']), 2)
        
        response = self.client.post(url, {'keyword': '2020/42'})
        self.failUnless(response.status_code, 200)
        print response.context['unscheduled_submissions']
        self.failUnlessEqual(len(response.context['unscheduled_submissions']), 1)

        response = self.client.post(url, {'keyword': '42/2020'})
        self.failUnless(response.status_code, 200)
        self.failUnlessEqual(len(response.context['unscheduled_submissions']), 1)
        