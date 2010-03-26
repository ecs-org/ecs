# -*- coding: utf-8 -*-
import os
import reversion

from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str

# metaclassen:
#  master control programm model:
#   date, time, user, uuid,  
class Workflow(models.Model):
    pass

class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

def upload_document_to(instance=None, filename=None):
    # file path is derived from the uuid_document_revision
    # FIXME: handle file name collisions
    dirs = list(instance.uuid_document_revision[:6]) + [instance.uuid_document_revision]
    return os.path.join(settings.FILESTORE, *dirs)

class DocumentFileStorage(FileSystemStorage):
    def path(self, name):
        # We need to overwrite the default behavior, because django won't let us save documents outside of MEDIA_ROOT
        return smart_str(os.path.normpath(name))

class Document(models.Model):
    uuid_document = models.SlugField(max_length=32)
    uuid_document_revision = models.SlugField(max_length=32)
    file = models.FileField(null=True, upload_to=upload_document_to, storage=DocumentFileStorage())
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    doctype = models.ForeignKey(DocumentType, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')

    version = models.CharField(max_length=250)
    date = models.DateTimeField()
    deleted = models.BooleanField(default=False, blank=True)
    
    def save(self, **kwargs):
        if self.file:
            import hashlib
            s = self.file.read()  # TODO optimize for large files! check if correct for binary files (e.g. random bytes)
            m = hashlib.md5()
            m.update(s)
            self.file.seek(0)
            self.uuid_document = m.hexdigest()
            self.uuid_document_revision = self.uuid_document
        return super(Document, self).save(**kwargs)


class EthicsCommission(models.Model):
    name = models.CharField(max_length=120)
    address_1 = models.CharField(max_length=120)
    address_2 = models.CharField(max_length=120)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=80)
    contactname = models.CharField(max_length=120, null=True)
    chairperson = models.CharField(max_length=120, null=True)
    email = models.EmailField(null=True)
    url = models.URLField(null=True)
    phone = models.CharField(max_length=60, null=True)
    fax = models.CharField(max_length=60, null=True)
    
    def __unicode__(self):
        return self.name

class SubmissionForm(models.Model):
    submission = models.ForeignKey("Submission", related_name="forms")
    documents = models.ManyToManyField(Document)
    ethics_commissions = models.ManyToManyField(EthicsCommission, related_name='submission_forms', through='Investigator')

    project_title = models.TextField()
    eudract_number = models.CharField(max_length=40, null=True)
    
    # 1.4 (via self.documents)

    # 1.5
    sponsor_name = models.CharField(max_length=80, null=True)
    sponsor_contactname = models.CharField(max_length=80, null=True)
    sponsor_address1 = models.CharField(max_length=60, null=True)
    sponsor_address2 = models.CharField(max_length=60, null=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=40, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True)
    sponsor_email = models.EmailField(null=True)

    invoice_name = models.CharField(max_length=80, null=True, blank=True)
    invoice_contactname = models.CharField(max_length=80, null=True, blank=True)
    invoice_address1 = models.CharField(max_length=60, null=True, blank=True)
    invoice_address2 = models.CharField(max_length=60, null=True, blank=True)
    invoice_zip_code = models.CharField(max_length=10, null=True, blank=True)
    invoice_city = models.CharField(max_length=40, null=True, blank=True)
    invoice_phone = models.CharField(max_length=30, null=True, blank=True)
    invoice_fax = models.CharField(max_length=30, null=True, blank=True)
    invoice_email = models.EmailField(null=True, blank=True)
    invoice_uid = models.CharField(max_length=30, null=True, blank=True) # 24? need to check
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
    subject_duration = models.CharField(max_length=20)
    subject_duration_active = models.CharField(max_length=20)
    subject_duration_controls = models.CharField(max_length=20)

    # 2.12
    subject_planned_total_duration = models.CharField(max_length=20)

    # 3a
    # FIXME: substance_registered_in_countries should be a ManyToManyField(Country)
    substance_registered_in_countries = models.CharField(max_length=300, null=True, blank=True) # comma seperated 2 letter codes.
    substance_preexisting_clinical_tries = models.NullBooleanField(blank=True)
    # FIXME: substance_p_c_t_countries should be a ManyToManyField(Country)
    substance_p_c_t_countries = models.CharField(max_length=300, null=True, blank=True) # comma seperated 2 letter codes.
    substance_p_c_t_phase = models.CharField(max_length=10, null=True, blank=True)
    substance_p_c_t_period = models.TextField(null=True, blank=True)
    substance_p_c_t_application_type = models.CharField(max_length=40, null=True, blank=True)
    substance_p_c_t_gcp_rules = models.NullBooleanField(blank=True)
    substance_p_c_t_final_report = models.NullBooleanField(blank=True)
    
    # 3b (via NonTestedUsedDrugs)
    
    # 4.x
    medtech_product_name = models.CharField(max_length=80, null=True, blank=True)
    medtech_manufacturer = models.CharField(max_length=80, null=True, blank=True)
    medtech_certified_for_exact_indications = models.NullBooleanField(blank=True)
    medtech_certified_for_other_indications = models.NullBooleanField(blank=True)
    medtech_ce_symbol = models.NullBooleanField(blank=True)
    medtech_manual_included = models.NullBooleanField(blank=True)
    medtech_technical_safety_regulations = models.TextField(null=True, blank=True)
    medtech_departure_from_regulations = models.TextField(null=True, blank=True)
    
    # 5.x
    insurance_name = models.CharField(max_length=60, null=True, blank=True)
    insurance_address_1 = models.CharField(max_length=80, null=True, blank=True)
    insurance_phone = models.CharField(max_length=30, null=True, blank=True)
    insurance_contract_number = models.CharField(max_length=60, null=True, blank=True)
    insurance_validity = models.CharField(max_length=60, null=True, blank=True)
    
    # 6.1 + 6.2 (via Measure)

    # 6.3
    additional_therapy_info = models.TextField()

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
    german_dataaccess_info = models.TextField(null=True)
    german_financing_info = models.TextField(null=True)
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
    study_plan_alpha = models.CharField(max_length=40)
    study_plan_power = models.CharField(max_length=40)
    study_plan_statalgorithm = models.CharField(max_length=40)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=40)
    study_plan_dropout_ratio = models.CharField(max_length=40)
    
    # 8.3
    study_plan_population_intention_to_treat  = models.BooleanField()
    study_plan_population_per_protocol  = models.BooleanField()
    study_plan_abort_crit = models.CharField(max_length=40)
    study_plan_planned_statalgorithm = models.CharField(max_length=40)

    # 8.4
    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    # 8.5
    study_plan_biometric_planning = models.CharField(max_length=120)
    study_plan_statistics_implementation = models.CharField(max_length=120)

    # 8.6 (either anonalgorith or reason or dvr may be set.)
    study_plan_dataprotection_reason = models.CharField(max_length=120, blank=True)
    study_plan_dataprotection_dvr = models.CharField(max_length=12, blank=True)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True, blank=True)
    
    # 9.x
    submitter_name = models.CharField(max_length=80)
    submitter_organisation = models.CharField(max_length=80)
    submitter_jobtitle = models.CharField(max_length=80)
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
    def protocol_number(self):
        protocol_doc = self.documents.filter(deleted=False, doctype__name='Protokoll').order_by('-date', '-version')[:1]
        if protocol_doc:
            return protocol_doc[0].version
        else:
            return None


class Investigator(models.Model):
    # FIXME: rename to `submission_form`
    submission = models.ForeignKey(SubmissionForm, related_name='investigators')
    ethics_commission = models.ForeignKey(EthicsCommission, null=True, related_name='investigators')
    main = models.BooleanField(default=False, blank=True)

    name = models.CharField(max_length=80)
    organisation = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    jus_practicandi = models.BooleanField(default=False, blank=True)
    specialist = models.CharField(max_length=80, blank=True)
    certified = models.BooleanField(default=False, blank=True)
    subject_count = models.IntegerField()
    sign_date = models.DateField()


class InvestigatorEmployee(models.Model):
    # FIXME: rename to `investigator`
    # TODO: check FIXME above
    submission = models.ForeignKey(Investigator)

    sex = models.CharField(max_length=1, choices=[("m", "male"), ("f", "female"), ("?", "")])
    title = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)


# 6.1 + 6.2
class Measure(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='measures')
    
    #FIXME: category should not be nullable
    category = models.CharField(max_length=3, null=True, choices=[('6.1', u"ausschließlich studienbezogen"), ('6.2', u"zu Routinezwecken")])
    type = models.CharField(max_length=30)
    count = models.TextField()
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)

# 3b
class NonTestedUsedDrug(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)

# 2.6.2 + 2.7
class ForeignParticipatingCenter(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)
    
    name = models.CharField(max_length=60)
    address_1 = models.CharField(max_length=60)
    address_2 = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=40)
    # FIXME: country should be a ForeignKey(Country)
    country = models.CharField(max_length=4)
    

class Amendment(models.Model):
    # FIXME: rename to `submission_form`
    submissionform = models.ForeignKey(SubmissionForm)
    order = models.IntegerField()
    number = models.CharField(max_length=40)
    date = models.DateField()

class NotificationType(models.Model):
    name = models.CharField(max_length=80, unique=True)
    form = models.CharField(max_length=80, default='ecs.core.forms.NotificationForm')
    model = models.CharField(max_length=80, default='ecs.core.models.Notification')
    
    @property
    def form_cls(self):
        if not hasattr(self, '_form_cls'):
            module, cls_name = self.form.rsplit('.', 1)
            self._form_cls = getattr(import_module(module), cls_name)
        return self._form_cls
    
    def __unicode__(self):
        return self.name

class Notification(models.Model):
    type = models.ForeignKey(NotificationType, null=True, related_name='notifications')
    investigators = models.ManyToManyField(Investigator, related_name='notifications')
    submission_forms = models.ManyToManyField(SubmissionForm, related_name='notifications')
    documents = models.ManyToManyField(Document)

    comments = models.TextField(default="", blank=True)
    date_of_receipt = models.DateField(null=True, blank=True)
    
    def __unicode__(self):
        return u"%s" % (self.type,)

class ReportNotification(Notification):
    reason_for_not_started = models.TextField(null=True, blank=True)
    recruited_subjects = models.IntegerField(null=True, blank=True)
    finished_subjects = models.IntegerField(null=True, blank=True)
    aborted_subjects = models.IntegerField(null=True, blank=True)
    SAE_count = models.PositiveIntegerField(default=0, blank=True)
    SUSAR_count = models.PositiveIntegerField(default=0, blank=True)
    
    class Meta:
        abstract = True

class CompletionReportNotification(ReportNotification):
    study_aborted = models.BooleanField()
    completion_date = models.DateField()
    
class ProgressReportNotification(ReportNotification):
    runs_till = models.DateField(null=True, blank=True)
    extension_of_vote_requested = models.BooleanField(default=False, blank=True)


class Checklist(models.Model):
    pass

class VoteReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Vote(models.Model):
    votereview = models.ForeignKey(VoteReview)
    submissionform = models.ForeignKey(SubmissionForm, null=True)
    checklists = models.ManyToManyField(Checklist)
    workflow = models.ForeignKey(Workflow)

class SubmissionReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Submission(models.Model):
    ec_number = models.CharField(max_length=50, null=True, blank=True)
    submissionreview = models.ForeignKey(SubmissionReview, null=True)
    vote = models.ForeignKey(Vote, null=True)
    workflow = models.ForeignKey(Workflow, null=True)

class NotificationAnswer(models.Model):
    workflow = models.ForeignKey(Workflow)
 
class Meeting(models.Model):
    submissions = models.ManyToManyField(Submission)
"""
class Revision(models.Model):
    pass

class Message(models.Model):
    pass

class AuditLog(models.Model):
    pass


class User(models.Model):
    pass

class Reviewer(models.Model):
    pass

class Annotation(models.Model):
    pass
"""

# Register models conditionally to avoid `already registered` errors when this module gets loaded twice.
if not reversion.is_registered(Amendment):
    reversion.register(Amendment) 
    reversion.register(Checklist) 
    reversion.register(Measure) 
    reversion.register(Document) 
    reversion.register(EthicsCommission) 
    reversion.register(Meeting) 
    reversion.register(ForeignParticipatingCenter) 
    reversion.register(Submission) 
    reversion.register(SubmissionForm) 
    reversion.register(SubmissionReview) 
    reversion.register(NonTestedUsedDrug) 
    reversion.register(NotificationAnswer) 
    reversion.register(Notification) 
    reversion.register(CompletionReportNotification) 
    reversion.register(ProgressReportNotification)
    reversion.register(Investigator) 
    reversion.register(InvestigatorEmployee) 
    reversion.register(Vote) 
    reversion.register(VoteReview) 
    reversion.register(Workflow)
