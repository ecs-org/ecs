# -*- coding: utf-8 -*-
import datetime
import urlparse
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models.signals import post_save
from django.conf import settings
from ecs.core.models.voting import FINAL_VOTE_RESULTS

from ecs.communication.models import Message, Thread
from ecs.meetings.models import TimetableEntry, Meeting
from ecs.documents.models import Document

from ecs import authorization
from ecs.authorization.managers import AuthorizationManager

class Submission(models.Model):
    ec_number = models.CharField(max_length=50, null=True, blank=True, unique=True, db_index=True) # e.g.: 2010/0345
    medical_categories = models.ManyToManyField('core.MedicalCategory', related_name='submissions', blank=True)
    thesis = models.NullBooleanField()
    retrospective = models.NullBooleanField()
    # FIXME: why do we have two field for expedited_review?
    expedited = models.NullBooleanField()
    expedited_review_categories = models.ManyToManyField('core.ExpeditedReviewCategory', related_name='submissions', blank=True)
    # FIXME: why do we have two fields for external_review?
    external_reviewer = models.NullBooleanField()
    external_reviewer_name = models.ForeignKey('auth.user', null=True, blank=True, related_name='reviewed_submissions')
    external_reviewer_billed_at = models.DateTimeField(null=True, default=None, blank=True, db_index=True)
    remission = models.BooleanField(default=False)    
    additional_reviewers = models.ManyToManyField(User, blank=True, related_name='additional_review_submission_set')
    sponsor_required_for_next_meeting = models.BooleanField(default=False)
    befangene = models.ManyToManyField(User, null=True, related_name='befangen_for_submissions')
    billed_at = models.DateTimeField(null=True, default=None, blank=True, db_index=True)
    
    is_amg = models.NullBooleanField()   # Arzneimittelgesetz
    is_mpg = models.NullBooleanField()   # Medizinproduktegesetz
    
    # denormalization
    current_submission_form = models.OneToOneField('core.SubmissionForm', null=True, related_name='_current_for')
    next_meeting = models.ForeignKey('meetings.Meeting', null=True, related_name='_current_for_submissions') # FIXME: this has to be updated dynamically to be useful
    
    objects = AuthorizationManager()

    def get_ec_number_display(self):
        try:
            year, ec_number = self.ec_number.split('/')
        except ValueError:
            return self.ec_number

        ec_number = ec_number.lstrip('0')
        if datetime.datetime.now().year == int(year):
            return ec_number
        else:
            return '%s/%s' % (ec_number, year)
    get_ec_number_display.short_description = 'EC-Number'

    def get_befangene(self):
        submission_form = self.get_most_recent_form()
        sponsor_email = submission_form.sponsor_email
        # FIXME: how to get submitter email?
        investigator_emails = [x.email for x in submission_form.investigators.all()]
        
        emails = [x for x in [sponsor_email]+investigator_emails if x]

        befangene = []
        for email in emails:
            try:
                users = User.objects.filter(email=email)
            except User.DoesNotExist:
                pass
            else:
                befangene += list(users)

        return befangene

    # FIXME: replace all calls with direct attribute access
    def get_most_recent_form(self):
        return self.current_submission_form
    
    # FIXME: replace all calls withs the appropriate direct attribute access
    def get_most_recent_vote(self):
        return self.current_submission_form.current_pending_vote or self.current_submission_form.current_published_vote
        
    @property
    def votes(self):
        from ecs.core.models import Vote
        return Vote.objects.filter(submission_form__submission=self)

    @property
    def project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.project_title
        
    @property
    def german_project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.german_project_title
        
    @property
    def multicentric(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.multicentric
        
    @property
    def is_active(self):
        submission_form = self.current_submission_form
        if submission_form:
            if submission_form.current_published_vote:
                return submission_form.current_published_vote.activates
        return False
        
    @property
    def main_ethics_commission(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.main_ethics_commission
        
    def save(self, **kwargs):
        if not self.ec_number:
            # FIXME: how do we really assign ec-numbers for new submissions?
            from random import randint
            self.ec_number = "EK-%s" % randint(10000, 100000)
        super(Submission, self).save(**kwargs)
        
    def __unicode__(self):
        return self.get_ec_number_display()
        
    class Meta:
        app_label = 'core'


class SubmissionQFactory(authorization.AuthorizationQFactory):
    def get_q(self, user):
        profile = user.get_profile()

        ### shortcircuit logic
        if not profile.approved_by_office:
            return self.make_deny_q()

        ### default policy: deny access to all submissions.
        q = self.make_deny_q()

        ### rules that apply until a final vote has been published.
        until_vote_q = self.make_q(additional_reviewers=user)
        if profile.thesis_review:
            until_vote_q |= self.make_q(thesis=True)
        if profile.board_member:
            until_vote_q |= self.make_q(timetable_entries__participations__user=user, timetable_entries__meeting=self.make_f('next_meeting'))
        if profile.expedited_review:
            until_vote_q |= self.make_q(expedited=True)
        if profile.external_review:
            until_vote_q |= self.make_q(external_reviewer_name=user)
        # FIXME: how do we detect whether an insurance review is required?
        #if profile.insurance_review:
        #    until_vote_q |= self.make_q(insurance_review_required=True)
        q |= until_vote_q & (
            self.make_q(current_submission_form__current_published_vote=None)
            | ~self.make_q(current_submission_form__current_published_vote__result__in=FINAL_VOTE_RESULTS)
        )

        ### rules that apply until the end of the submission lifecycle
        until_eol_q = self.make_q(pk__gt=0) # active=True
        if not (user.is_staff or profile.internal):
            until_eol_q &= self.make_q(current_submission_form__submitter=user) | self.make_q(current_submission_form__primary_investigator__user=user) | self.make_q(current_submission_form__sponsor=user)
        q |= until_eol_q
        return q

authorization.register(Submission, SubmissionQFactory)

class NameField(object):
    def contribute_to_class(self, cls, name):
        fields = {
            'gender': models.CharField(max_length=1, choices=(('f', 'Frau'), ('m', 'Herr')), blank=True, null=True),
            'first_name': models.CharField(max_length=50, blank=True),
            'last_name': models.CharField(max_length=50, blank=True),
        }
        for fieldname, field in fields.items():
            field.contribute_to_class(cls, "%s_%s" % (name, fieldname))


class SubmissionForm(models.Model):
    submission = models.ForeignKey('core.Submission', related_name="forms")
    documents = GenericRelation(Document)
    ethics_commissions = models.ManyToManyField('core.EthicsCommission', related_name='submission_forms', through='Investigator')
    pdf_document = models.ForeignKey(Document, related_name="submission_forms", null=True)

    project_title = models.TextField()
    eudract_number = models.CharField(max_length=60, null=True)
    
    # denormalization
    primary_investigator = models.OneToOneField('core.Investigator', null=True)
    current_published_vote = models.OneToOneField('core.Vote', null=True, related_name='_currently_published_for')
    current_pending_vote = models.OneToOneField('core.Vote', null=True, related_name='_currently_pending_for')

    class Meta:
        app_label = 'core'
        
    objects = AuthorizationManager('submission')
    
    # 1.4 (via self.documents)

    # 1.5
    sponsor = models.ForeignKey(User, null=True, related_name="sponsored_submission_forms")
    sponsor_name = models.CharField(max_length=100, null=True)
    sponsor_contact = NameField()
    sponsor_address1 = models.CharField(max_length=60, null=True)
    sponsor_address2 = models.CharField(max_length=60, null=True, blank=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=80, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True)
    sponsor_email = models.EmailField(null=True)
    
    invoice_name = models.CharField(max_length=160, null=True, blank=True)
    invoice_contact = NameField()
    invoice_address1 = models.CharField(max_length=60, null=True, blank=True)
    invoice_address2 = models.CharField(max_length=60, null=True, blank=True)
    invoice_zip_code = models.CharField(max_length=10, null=True, blank=True)
    invoice_city = models.CharField(max_length=80, null=True, blank=True)
    invoice_phone = models.CharField(max_length=50, null=True, blank=True)
    invoice_fax = models.CharField(max_length=45, null=True, blank=True)
    invoice_email = models.EmailField(null=True, blank=True)
    invoice_uid = models.CharField(max_length=35, null=True, blank=True) # 24? need to check
    invoice_uid_verified_level1 = models.DateTimeField(null=True, blank=True) # can be done via EU API
    invoice_uid_verified_level2 = models.DateTimeField(null=True, blank=True) # can be done manually via Tax Authority, local.
    # TODO: invoice_uid_verified_level2 should also have a field who handled the level2 verification.
    
    # 2.1
    project_type_non_reg_drug = models.BooleanField()
    project_type_reg_drug = models.BooleanField()
    project_type_reg_drug_within_indication = models.BooleanField()
    project_type_reg_drug_not_within_indication = models.BooleanField()
    project_type_medical_method = models.BooleanField()
    project_type_medical_device = models.BooleanField()
    project_type_medical_device_with_ce = models.BooleanField()
    project_type_medical_device_without_ce = models.BooleanField()
    project_type_medical_device_performance_evaluation = models.BooleanField()
    project_type_basic_research = models.BooleanField()
    project_type_genetic_study = models.BooleanField()
    project_type_register = models.BooleanField()
    project_type_biobank = models.BooleanField()
    project_type_retrospective = models.BooleanField()
    project_type_questionnaire = models.BooleanField()
    project_type_education_context = models.SmallIntegerField(null=True, blank=True, choices=[(1, 'Dissertation'), (2, 'Diplomarbeit')])
    project_type_misc = models.TextField(null=True, blank=True)
    project_type_psychological_study = models.BooleanField()
    
    # 2.2
    # FIXME: use fixed set of choices ?
    specialism = models.TextField(null=True)

    # 2.3
    pharma_checked_substance = models.TextField(null=True, blank=True)
    pharma_reference_substance = models.TextField(null=True, blank=True)
    
    # 2.4
    medtech_checked_product = models.TextField(null=True, blank=True)
    medtech_reference_substance = models.TextField(null=True, blank=True)

    # 2.5
    clinical_phase = models.CharField(max_length=10)
    
    # 2.6 + 2.7 (via ParticipatingCenter)
    
    # 2.8
    already_voted = models.BooleanField()
    
    # 2.9
    subject_count = models.IntegerField()

    # 2.10
    subject_minage = models.IntegerField()
    subject_maxage = models.IntegerField()
    subject_noncompetents = models.BooleanField()
    subject_males = models.BooleanField()    
    subject_females = models.BooleanField()
    subject_childbearing = models.BooleanField()
    
    # 2.11
    subject_duration = models.CharField(max_length=200)
    subject_duration_active = models.CharField(max_length=200)
    subject_duration_controls = models.CharField(max_length=200)

    # 2.12
    subject_planned_total_duration = models.CharField(max_length=250)

    # 3a
    substance_registered_in_countries = models.ManyToManyField('countries.Country', related_name='submission_forms', blank=True, db_table='submission_registered_countries')
    substance_preexisting_clinical_tries = models.NullBooleanField(blank=True, db_column='existing_tries')
    substance_p_c_t_countries = models.ManyToManyField('countries.Country', blank=True)
    substance_p_c_t_phase = models.CharField(max_length=80, null=True, blank=True)
    substance_p_c_t_period = models.TextField(null=True, blank=True)
    substance_p_c_t_application_type = models.CharField(max_length=145, null=True, blank=True)
    substance_p_c_t_gcp_rules = models.NullBooleanField(blank=True)
    substance_p_c_t_final_report = models.NullBooleanField(blank=True)
    
    # 3b (via NonTestedUsedDrugs)
    
    # 4.x
    medtech_product_name = models.CharField(max_length=210, null=True, blank=True)
    medtech_manufacturer = models.CharField(max_length=80, null=True, blank=True)
    medtech_certified_for_exact_indications = models.NullBooleanField(blank=True)
    medtech_certified_for_other_indications = models.NullBooleanField(blank=True)
    medtech_ce_symbol = models.NullBooleanField(blank=True)
    medtech_manual_included = models.NullBooleanField(blank=True)
    medtech_technical_safety_regulations = models.TextField(null=True, blank=True)
    medtech_departure_from_regulations = models.TextField(null=True, blank=True)
    
    # 5.x
    insurance_name = models.CharField(max_length=125, null=True, blank=True)
    insurance_address_1 = models.CharField(max_length=80, null=True, blank=True)
    insurance_phone = models.CharField(max_length=30, null=True, blank=True)
    insurance_contract_number = models.CharField(max_length=60, null=True, blank=True)
    insurance_validity = models.CharField(max_length=60, null=True, blank=True)
    
    # 6.1 + 6.2 (via Measure)

    # 6.3
    additional_therapy_info = models.TextField(blank=True)

    # 7.x
    german_project_title = models.TextField(null=True)
    german_summary = models.TextField(null=True)
    german_preclinical_results = models.TextField(null=True)
    german_primary_hypothesis = models.TextField(null=True)
    german_inclusion_exclusion_crit = models.TextField(null=True)
    german_ethical_info = models.TextField(null=True)
    german_protected_subjects_info = models.TextField(null=True)
    german_recruitment_info = models.TextField(null=True)
    german_consent_info = models.TextField(null=True)
    german_risks_info = models.TextField(null=True)
    german_benefits_info = models.TextField(null=True)
    german_relationship_info = models.TextField(null=True)
    german_concurrent_study_info = models.TextField(null=True)
    german_sideeffects_info = models.TextField(null=True)
    german_statistical_info = models.TextField(null=True, blank=True)
    german_dataprotection_info = models.TextField(null=True, blank=True)
    german_aftercare_info = models.TextField(null=True)
    german_payment_info = models.TextField(null=True)
    german_abort_info = models.TextField(null=True)
    german_dataaccess_info = models.TextField(null=True, blank=True)
    german_financing_info = models.TextField(null=True, blank=True)
    german_additional_info = models.TextField(null=True, blank=True)
    
    # 8.1
    # FIXME: study_plan_blind should not be nullable
    study_plan_blind = models.SmallIntegerField(null=True, choices=[(0, 'offen'), (1, 'blind'), (2, 'doppelblind')])
    study_plan_observer_blinded = models.BooleanField()
    study_plan_randomized = models.BooleanField()
    study_plan_parallelgroups = models.BooleanField()
    study_plan_controlled = models.BooleanField()
    study_plan_cross_over = models.BooleanField()
    study_plan_placebo = models.BooleanField()
    study_plan_factorized = models.BooleanField()
    study_plan_pilot_project = models.BooleanField()
    study_plan_equivalence_testing = models.BooleanField()
    study_plan_misc = models.TextField(null=True, blank=True)
    study_plan_number_of_groups = models.TextField(null=True, blank=True)
    study_plan_stratification = models.TextField(null=True, blank=True)
    study_plan_sample_frequency = models.TextField(null=True, blank=True) 
    study_plan_primary_objectives = models.TextField(null=True, blank=True)
    study_plan_null_hypothesis = models.TextField(null=True, blank=True)
    study_plan_alternative_hypothesis = models.TextField(null=True, blank=True)
    study_plan_secondary_objectives = models.TextField(null=True, blank=True)

    # 8.2
    study_plan_alpha = models.CharField(max_length=80)
    study_plan_power = models.CharField(max_length=80)
    study_plan_statalgorithm = models.CharField(max_length=50)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=100)
    study_plan_dropout_ratio = models.CharField(max_length=80)
    
    # 8.3
    study_plan_population_intention_to_treat  = models.BooleanField()
    study_plan_population_per_protocol  = models.BooleanField()
    study_plan_abort_crit = models.CharField(max_length=265)
    study_plan_planned_statalgorithm = models.TextField(null=True, blank=True)

    # 8.4
    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    # 8.5
    study_plan_biometric_planning = models.CharField(max_length=260)
    study_plan_statistics_implementation = models.CharField(max_length=270)

    # 8.6 (either anonalgorith or reason or dvr may be set.)
    study_plan_dataprotection_reason = models.CharField(max_length=120, blank=True)
    study_plan_dataprotection_dvr = models.CharField(max_length=180, blank=True)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True, blank=True)
    
    # 9.x
    submitter = models.ForeignKey(User, null=True, related_name='submitted_submission_forms')
    submitter_contact = NameField()
    submitter_organisation = models.CharField(max_length=180)
    submitter_jobtitle = models.CharField(max_length=130)
    submitter_is_coordinator = models.BooleanField()
    submitter_is_main_investigator = models.BooleanField()
    submitter_is_sponsor = models.BooleanField()
    submitter_is_authorized_by_sponsor = models.BooleanField()
    submitter_agrees_to_publishing = models.BooleanField(default=True)
    
    date_of_receipt = models.DateField(null=True, blank=True)
   
    def __unicode__(self):
        return "%s: %s" % (self.submission.ec_number, self.project_title)
    
    @property
    def multicentric(self):
        return self.investigators.count() > 1
        
    @property
    def monocentric(self):
        return self.investigators.count() == 1
        
    @property
    def study_plan_open(self):
        return self.study_plan_blind == 0

    @property
    def study_plan_single_blind(self):
        return self.study_plan_blind == 1

    @property
    def study_plan_double_blind(self):
        return self.study_plan_blind == 2
        
    @property
    def protocol(self):
        protocol_doc = self.documents.filter(deleted=False, doctype__name='Protokoll').order_by('-date', '-version')[:1]
        if protocol_doc:
            return protocol_doc[0]
        else:
            return None

    @property
    def protocol_number(self):
        protocol_doc = self.documents.filter(deleted=False, doctype__name='Protokoll').order_by('-date', '-version')[:1]
        if protocol_doc:
            return protocol_doc[0].version
        else:
            return None

    @property
    def project_type_education_context_phd(self):
        return self.project_type_education_context == 1

    @property
    def project_type_education_context_master(self):
        return self.project_type_education_context == 2

    @property
    def measures_study_specific(self):
        return self.measures.filter(category="6.1")
    
    @property
    def measures_nonspecific(self):
        return self.measures.filter(category="6.2")
        
    @property
    def main_ethics_commission(self):
        try:
            return self.primary_investigator.ethics_commission
        except Investigator.DoesNotExist:
            return None

def _post_submission_form_save(**kwargs):
    new_sf = kwargs['instance']
    submission = new_sf.submission
    
    old_sf = submission.current_submission_form
    submission.current_submission_form = new_sf
    submission.save(force_update=True)
    
    if not old_sf:
        return
    
    recipients = []
    for username in settings.DIFF_REVIEW_LIST:
        try:
            recipients.append(User.objects.get(username=username))
        except User.DoesNotExist:
            # FIXME: when we run unittests, these users may not exist.
            pass

    timetable_entries = TimetableEntry.objects.filter(submission=submission)
    recipients += sum([list(x.users) for x in timetable_entries], [])

    meetings = set([x.meeting for x in timetable_entries])
    assigned_medical_categories = [x.category for x in sum([list(x.medical_categories.all()) for x in meetings], []) if x.category in submission.medical_categories.all()]
    recipients += sum([list(x.board_members) for x in assigned_medical_categories], [])
    recipients += list(User.objects.filter(email__in=[old_sf.sponsor_email, new_sf.sponsor_email]))
    recipients += list(User.objects.filter(email__in=sum([[x.email for x in old_sf.investigators.all()], [x.email for x in new_sf.investigators.all()]], [])))

    recipients = set(recipients)

    text = u'An der Studie EK-Nr. %s wurden Änderungen durchgeführt.\n' % new_sf.submission.ec_number
    url = reverse('ecs.core.views.diff', kwargs={'old_submission_form_pk': old_sf.pk, 'new_submission_form_pk': new_sf.pk})
    text += u'Um sie anzusehen klicken sie <a href="#" onclick="window.parent.location.href=\'%s\';">hier</a>.' % url
    subject = u'Änderungen an %s' % new_sf.submission.ec_number

    for recipient in recipients:
        thread, created = Thread.objects.get_or_create(
            subject=subject,
            sender=User.objects.get(username='root'),
            receiver=recipient,
            submission=new_sf.submission
        )

        message = thread.add_message(User.objects.get(username='root'), text=text)

post_save.connect(_post_submission_form_save, sender=SubmissionForm)

class Investigator(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='investigators')
    ethics_commission = models.ForeignKey('core.EthicsCommission', null=True, related_name='investigators')
    main = models.BooleanField(default=False, blank=True)

    user = models.ForeignKey(User, null=True, related_name='investigations')
    contact = NameField()
    organisation = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    jus_practicandi = models.BooleanField(default=False, blank=True)
    specialist = models.CharField(max_length=80, blank=True)
    certified = models.BooleanField(default=False, blank=True)
    subject_count = models.IntegerField()
    
    objects = AuthorizationManager('submission_form__submission')
    
    class Meta:
        app_label = 'core'


def _post_investigator_save(sender, **kwargs):
    investigator = kwargs['instance']
    if not investigator.main:
        return
    investigator.submission_form.primary_investigator = investigator
    investigator.submission_form.save()
    
post_save.connect(_post_investigator_save, sender=Investigator)

class InvestigatorEmployee(models.Model):
    investigator = models.ForeignKey(Investigator, related_name='employees')

    sex = models.CharField(max_length=1, choices=[("m", "Herr"), ("f", "Frau"), ("?", "")])
    title = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)
    
    objects = AuthorizationManager('investigator__submission_form__submission')
    
    class Meta:
        app_label = 'core'
    
    @property
    def full_name(self):
        name = []
        if self.title:
            name.append(self.title)
        if self.firstname:
            name.append(self.firstname)
        if self.surname:
            name.append(self.surname)
        return " ".join(name)
    
    @property
    def geschlecht_string(self):
        return dict(m="Hr", f="Fr").get(self.sex, "")


# 6.1 + 6.2
class Measure(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='measures')
    
    #FIXME: category should not be nullable
    category = models.CharField(max_length=3, null=True, choices=[('6.1', u"ausschließlich studienbezogen"), ('6.2', u"zu Routinezwecken")])
    type = models.CharField(max_length=150)
    count = models.CharField(max_length=150)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)
    
    objects = AuthorizationManager('submission_form__submission')
    
    class Meta:
        app_label = 'core'


# 3b
class NonTestedUsedDrug(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)
    
    objects = AuthorizationManager('submission_form__submission')
    
    class Meta:
        app_label = 'core'


# 2.6.2 + 2.7
class ForeignParticipatingCenter(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)
    name = models.CharField(max_length=60)
    investigator_name = models.CharField(max_length=60, blank=True)
    
    objects = AuthorizationManager('submission_form__submission')
    
    class Meta:
        app_label = 'core'

