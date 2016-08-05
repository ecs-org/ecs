import os
import json
from urllib.parse import urlsplit

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from ecs.utils.testcases import LoginTestCase
from ecs.core.tests.test_submissions import create_submission_form
from ecs.core.models import MedicalCategory
from ecs.core import bootstrap
from ecs.checklists import bootstrap as checklists_bootstrap
from ecs.core.models import SubmissionForm
from ecs.core.models import EthicsCommission
from ecs.documents.models import DocumentType
from ecs.users.utils import get_or_create_user
from ecs.tasks.models import Task

VALID_SUBMISSION_FORM_DATA = {
    'investigator-0-ethics_commission': ['1'], 'study_plan_abort_crit': ['Peto'], 'submitter_contact_title': ['Univ. Doz. Dr.'], 
    'study_plan_statistics_implementation': ['Mag. rer.soc.oec. Jane Doe / Statistikerin'], 'investigator-1-contact_last_name': ['Doe'], 
    'sponsor_fax': ['+430987654345678'], 'substance_p_c_t_final_report': ['2'], 'substance_registered_in_countries': ['AT','FR'], 
    'pharma_reference_substance': ['none'], 'medtech_product_name': [''], 'study_plan_alpha': ['0.03'], 
    'investigatoremployee-0-investigator_index': ['0'], 'study_plan_secondary_objectives': [''], 'eudract_number': ['2020-002323-99'], 
    'study_plan_dropout_ratio': ['0'], 'german_protected_subjects_info': ['bla bla bla'], 'sponsor_contact_gender': ['f'], 
    'study_plan_misc': [''], 'german_preclinical_results': ['bla bla bla'], 'study_plan_biometric_planning': ['Mag. rer.soc.oec. Jane Doe/ Statistikerin'], 
    'investigatoremployee-0-title': [''], 'nontesteduseddrug-INITIAL_FORMS': ['0'], 'submitter_contact_last_name': ['Doe'], 
    'investigatoremployee-0-sex': [''], 'study_plan_stratification': [''], 'german_recruitment_info': ['bla bla bla'], 
    'investigator-1-phone': [''], 'submitter_email': [''], 'invoice_uid': [''], 'nontesteduseddrug-0-preparation_form': [''], 
    'investigator-1-contact_first_name': ['John'], 'investigator-1-email': ['rofl@copter.com'], 'german_concurrent_study_info': ['bla bla bla'], 
    'study_plan_planned_statalgorithm': ['log rank test'], 'document-date': [''], 'medtech_reference_substance': [''], 'measure-MAX_NUM_FORMS': [''], 
    'study_plan_statalgorithm': ['none'], 'foreignparticipatingcenter-TOTAL_FORMS': ['1'], 'routinemeasure-MAX_NUM_FORMS': [''], 
    'invoice_contact_first_name': [''], 'investigator-0-mobile': [''], 'submitter_is_coordinator': ['on'], 'insurance_validity': ['keine'], 
    'sponsor_name': ['sponsor'], 'sponsor_contact_last_name': ['last'], 'sponsor_email': ['johndoe@example.com'], 'subject_duration': ['96 months'], 
    'submitter_contact_gender': ['f'], 'nontesteduseddrug-0-generic_name': [''], 'medtech_ce_symbol': ['3'], 'investigator-0-contact_gender': ['f'], 
    'investigator-1-contact_gender': ['m'], 'nontesteduseddrug-MAX_NUM_FORMS': [''], 'investigatoremployee-INITIAL_FORMS': ['0'], 'insurance_phone': ['1234567'], 
    'investigator-0-email': ['rofl@copter.com'], 'measure-TOTAL_FORMS': ['0'], 'medtech_manufacturer': [''], 'subject_planned_total_duration': ['10 months'], 
    'german_summary': ['Bei diesem Projekt handelt es sich um ein sowieso bla blu'], 'document-doctype': [''], 
    'investigator-0-contact_first_name': ['Jane'], 'nontesteduseddrug-0-dosage': [''], 'insurance_contract_number': ['2323'], 'study_plan_power': ['0.80'], 
    'sponsor_phone': ['+43 1 40170'], 'subject_maxage': ['21'], 'investigator-1-ethics_commission': [''], 'subject_noncompetents': ['on'], 
    'german_dataprotection_info': ['bla bla bla'], 'german_risks_info': ['bla bla bla'], 
    'german_ethical_info': ['bla bla bla'], 'foreignparticipatingcenter-0-id': [''], 'investigatoremployee-TOTAL_FORMS': ['1'], 
    'specialism': ['Immunologie'], 'investigator-1-subject_count': ['4'], 'medtech_certified_for_other_indications': ['3'], 
    'german_payment_info': ['bla bla bla'], 'investigator-0-contact_title': ['Univ. Doz. Dr.'], 
    'study_plan_dataprotection_anonalgoritm': ['Electronically generated unique patient number'], 
    'additional_therapy_info': ['long blabla'], 'german_inclusion_exclusion_crit': ['bla bla bla'], 
    'medtech_technical_safety_regulations': [''], 'foreignparticipatingcenter-MAX_NUM_FORMS': [''], 'german_aftercare_info': ['bla bla bla'], 
    'investigator-1-fax': [''], 'study_plan_null_hypothesis': [''], 'investigator-1-mobile': [''], 'invoice_address': [''], 
    'substance_preexisting_clinical_tries': ['2'], 'substance_p_c_t_phase': ['III'], 'subject_males': ['on'], 'investigator-0-phone': [''], 
    'substance_p_c_t_period': ['period'], 'german_benefits_info': ['bla bla bla'], 
    'german_abort_info': ['bla bla bla'], 'insurance_address': ['insurancestreet 1'], 'german_additional_info': ['bla bla bla'], 
    'investigatoremployee-MAX_NUM_FORMS': [''], 'investigatoremployee-0-organisation': [''], 'study_plan_primary_objectives': [''], 
    'study_plan_number_of_groups': [''], 'invoice_contact_last_name': [''], 'document-replaces_document': [''], 'investigator-TOTAL_FORMS': ['2'], 
    'study_plan_dataprotection_reason': [''], 'medtech_certified_for_exact_indications': ['3'], 'sponsor_city': ['Wien'], 'medtech_manual_included': ['3'], 
    'invoice_contact_gender': [''], 'foreignparticipatingcenter-INITIAL_FORMS': ['0'], 'study_plan_alternative_hypothesis': [''], 'medtech_checked_product': [''], 
    'study_plan_dataprotection_dvr': [''], 'investigator-0-fax': [''], 'investigator-0-specialist': [''], 'study_plan_sample_frequency': [''], 
    'investigator-1-contact_title': ['Maga.'], 'submission_type': '1', 'investigator-1-contact_origanisation': ['BlaBlu'],
    'study_plan_dataquality_checking': ['National coordinators'], 'project_type_nursing_study': ['on'],
    'project_type_non_reg_drug': ['on'], 'german_relationship_info': ['bla bla bla'], 'nontesteduseddrug-0-id': [''], 'project_title': ['FOOBAR POST Test'], 
    'invoice_fax': [''], 'investigator-MAX_NUM_FORMS': [''], 'sponsor_zip_code': ['2323'], 'subject_duration_active': ['14 months'], 
    'measure-INITIAL_FORMS': ['0'], 'nontesteduseddrug-TOTAL_FORMS': ['1'], 'already_voted': ['on'], 'subject_duration_controls': ['36 months'], 
    'invoice_phone': [''], 'submitter_jobtitle': ['jobtitle'], 'investigator-1-specialist': [''], 'german_sideeffects_info': ['bla bla bla'], 
    'subject_females': ['on'], 'investigator-0-organisation': ['orga'], 'sponsor_contact_first_name': ['first'],
    'pharma_checked_substance': ['1'], 'investigator-0-subject_count': ['1'], 'project_type_misc': [''], 
    'foreignparticipatingcenter-0-name': [''], 'investigator-1-organisation': ['orga'], 'invoice_city': [''], 'german_financing_info': ['bla bla bla'], 
    'submitter_contact_first_name': ['Jane'], 'foreignparticipatingcenter-0-investigator_name': [''], 'german_dataaccess_info': ['bla bla bla'], 
    'documents': [], 'sponsor_contact_title': [''], 'invoice_contact_title': [''], 
    'investigator-0-contact_last_name': ['Doe'], 'medtech_departure_from_regulations': [''], 
    'routinemeasure-TOTAL_FORMS': ['0'], 'invoice_zip_code': [''], 'routinemeasure-INITIAL_FORMS': ['0'], 'invoice_email': [''], 
    'csrfmiddlewaretoken': ['9d8077845a05603196d32bea1cf25c28'], 'investigatoremployee-0-surname': [''], 'study_plan_blind': ['0'], 
    'document-file': [''], 'study_plan_datamanagement': ['Date entry and management'], 
    'german_primary_hypothesis': ['bla bla bla'], 'subject_childbearing': ['on'], 'substance_p_c_t_countries': ['AT','DE','CH'], 
    'insurance_name': ['insurance'], 'project_type_education_context': [''], 'clinical_phase': ['II'], 
    'investigator-INITIAL_FORMS': ['1'], 'subject_count': ['190'], 'substance_p_c_t_gcp_rules': ['2'], 'subject_minage': ['0'], 
    'investigatoremployee-0-firstname': [''], 'german_consent_info': ['bla bla bla'], 'document-version': [''], 'substance_p_c_t_application_type': ['IV in children'], 
    'german_project_title': ['kjkjkjk'], 'submitter_organisation': ['submitter orga'], 'study_plan_multiple_test_correction_algorithm': ['Keines'], 
    'sponsor_address': ['sponsor address 1'], 'invoice_name': [''], 'german_statistical_info': ['bla bla bla'], 'submitter_email': ['submitter@example.com'],
    'study_plan_dataprotection_choice': ['non-personal'], 'investigator-0-main': ['on'], 'study_plan_alpha_sided': ['0'],
}

class SubmissionViewsTestCase(LoginTestCase):
    '''Several tests for different views of a submission form.
    
    Tests for accessibility and functioning of core submission-form views.
    '''
    
    def setUp(self):
        super().setUp()
        checklists_bootstrap.checklist_blueprints()
        bootstrap.ethics_commissions()
        VALID_SUBMISSION_FORM_DATA['investigator-0-ethics_commission'] = [str(EthicsCommission.objects.all()[0].pk)]
        VALID_SUBMISSION_FORM_DATA['investigator-1-ethics_commission'] = [str(EthicsCommission.objects.all()[0].pk)]

        self.office_user, created = get_or_create_user('unittest-office@example.org')
        self.office_user.set_password('password')
        self.office_user.save()
        office_group = Group.objects.get(name='EC-Office')
        self.office_user.groups.add(office_group)
        profile = self.office_user.profile
        profile.is_internal = True
        profile.save()

    def get_docstash_url(self):
        url = reverse('ecs.core.views.submissions.create_submission_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url = response['Location']
        return url
        
    def get_post_data(self, update=None):
        data = VALID_SUBMISSION_FORM_DATA.copy()
        data['document-doctype'] = str(DocumentType.objects.get(identifier='protocol').pk)
        if update:
            data.update(update)
        return data

    def test_create_submission_form(self):
        '''Tests if the docstash is reachable.
        Also tests document count and versioning of the docstash for a submissionform.
        '''
        
        url = self.get_docstash_url()
        
        # post some data
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        
        # from docstash
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        upload_url = url.replace('new', 'doc/upload', 1)    # XXX: ugly

        # document upload
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'menschenrechtserklaerung.pdf')
        with open(file_path, 'rb') as f:
            response = self.client.post(upload_url, self.get_post_data({
                'document-file': f,
                'document-name': 'Menschenrechtserklärung',
                'document-version': '3.1415',
                'document-date': '26.10.2010',
            }))
        self.assertEqual(response.status_code, 200)
        first_doc = response.context['documents'][0]
        self.assertEqual(first_doc.version, '3.1415')
        
        # replace document
        with open(file_path, 'rb') as f:
            response = self.client.post(upload_url, self.get_post_data({
                'document-file': f,
                'document-name': 'Menschenrechtserklärung',
                'document-version': '3',
                'document-date': '26.10.2010',
                'document-replaces_document': first_doc.pk,
            }))
        self.assertEqual(response.status_code, 200)
        docs = response.context['documents']
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].version, '3')
        
        # posting valid data
        response = self.client.post(url, self.get_post_data({'submit': 'submit', 'documents': [str(doc.pk) for doc in docs]}))
        self.assertEqual(response.status_code, 302)
        sf = SubmissionForm.objects.get(project_title='FOOBAR POST Test')
        self.assertEqual(sf.documents.count(), 1)
        self.assertEqual(sf.documents.all()[0].version, '3')
        
    def test_readonly_submission_form(self):
        '''Tests if the readonly submissionform is accessible.
        '''
        
        submission_form = create_submission_form()
        response = self.client.get(reverse('readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
        self.assertEqual(response.status_code, 200)

    def test_submission_pdf(self):
        '''Tests if a pdf can be produced out of a pre existing submissionform.
        '''

        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.core.views.submissions.submission_form_pdf', kwargs={'submission_form_pk': submission_form.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(next(response.streaming_content)[:5], b'%PDF-')

    def test_document_download(self):
        submission_form = create_submission_form()
        document_pk = submission_form.documents.get().pk
        response = self.client.get(reverse('ecs.core.views.submissions.download_document', kwargs={'submission_form_pk': submission_form.pk, 'document_pk': document_pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(next(response.streaming_content)[:5], b'%PDF-')

    def test_document_download_anyone(self):
        submission_form = create_submission_form()
        document_pk = submission_form.documents.get().pk

        user, created = get_or_create_user('someone@example.org')
        user.set_password('password')
        user.save()

        self.client.logout()
        self.client.login(email='someone@example.org', password='password')

        response = self.client.get(reverse('ecs.core.views.submissions.download_document', kwargs={'submission_form_pk': submission_form.pk, 'document_pk': document_pk}))
        self.assertEqual(response.status_code, 404)

    def test_submission_form_search(self):
        '''Tests if all submissions are searchable via the keyword argument.
        Tests that the correct count of submissions is returned by the search function.
        '''
        
        create_submission_form(20200001)
        create_submission_form(20200042)
        create_submission_form(20209942)
        url = reverse('ecs.core.views.submissions.all_submissions')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.count()]), 3)
        
        response = self.client.get(url, {'keyword': '42'})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.exists()]), 1)

        response = self.client.get(url, {'keyword': '42/2020'})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.exists()]), 1)
        
    def test_submission_form_copy(self):
        '''Tests if a submissionform can be copied. Compares initial version against copied version.
        '''
        
        submission_form = create_submission_form(presenter=self.user)
        response = self.client.get(reverse('ecs.core.views.submissions.copy_latest_submission_form', kwargs={'submission_pk': submission_form.submission.pk}))
        self.assertEqual(response.status_code, 302)
        url = reverse('ecs.core.views.submissions.copy_submission_form', kwargs={'submission_form_pk': submission_form.pk})
        self.assertEqual(url, urlsplit(response['Location']).path)
    
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        target_url = response['Location']
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial.get('project_title'), submission_form.project_title)

    def test_initial_review(self):
        submission_form = create_submission_form(presenter=self.user)

        self.client.logout()
        self.client.login(email=self.office_user.email, password='password')

        task = Task.objects.for_data(submission_form.submission).get(task_type__workflow_node__uid='initial_review')
        refetch = lambda: Task.objects.get(pk=task.pk)

        # accept initial review task
        response = self.client.post(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        self.assertEqual(response.status_code, 302)
        task = refetch()
        self.assertEqual(self.office_user, task.assigned_to)

        url = task.url

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # delegate the task back to the pool
        reponse = self.client.post(url, {'task_management-action': 'delegate', 'task_management-assign_to': '', 'task_management-submit': 'submit'})
        task = refetch()
        self.assertEqual(None, task.assigned_to)

        # accept the task again
        response = self.client.post(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        self.assertEqual(response.status_code, 302)
        task = refetch()
        self.assertEqual(self.office_user, task.assigned_to)

        # complete the task
        reponse = self.client.post(url, {'task_management-action': 'complete_0', 'task_management-submit': 'submit'})
        task = refetch()
        self.assertTrue(task.closed_at is not None)

        self.client.logout()
        self.client.login(email=self.user.email, password='password')
