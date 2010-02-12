# -*- coding: utf-8 -*- 


from django.db import models
from django.contrib.auth.models import User

# metaclassen:
#  master control programm model:
#   date, time, user, uuid,  
class Workflow(models.Model):
    pass

class Document(models.Model):
    uuid_document = models.SlugField(max_length=32)
    # file path is derived from the uuid_document_revision
    uuid_document_revision = models.SlugField(max_length=32)

    version = models.CharField(max_length=20)
    date = models.DateTimeField()

    # this document is only being refered to, but it does not exist physically in the system:
    absent = models.BooleanField()

    # FileField might be enough, OTOH we'll have really many files.
    # So a more clever way of storage might be useful.
    def _filename(self):
        import settings, os
        
        dirs = list(self.uuid_document_revision)[0:6] + [self.uuid_document_revision]
        filename = os.path.join(settings.FILESTORE, *dirs)
        dirname = os.path.dirname(filename)
        try:
            os.makedirs(dirname)
        except os.error:
            pass                
        return filename

    def open(self, mode):
        """returns a binary file object for reading/writing of the document depending upon mode"""
        return open(self._filename(), mode)


class EthicsCommission(models.Model):
    name = models.CharField(max_length=60)
    address_1 = models.CharField(max_length=60)
    address_2 = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=40)

class InvolvedCommissionsForSubmission(models.Model):
    commission = models.ForeignKey(EthicsCommission)
    submission = models.ForeignKey("SubmissionForm")
    # is this the main commission?
    main = models.BooleanField()
    examiner_name = models.CharField(max_length=120, default="")

class InvolvedCommissionsForNotification(models.Model):
    commission = models.ForeignKey(EthicsCommission)
    submission = models.ForeignKey("NotificationForm")
    # is this the main commission?
    main = models.BooleanField()
    examiner_name = models.CharField(max_length=120, default="")


class SubmissionForm(models.Model):
    project_title = models.CharField(max_length=120)
    protocol_number = models.CharField(max_length=40, null=True)
    date_of_protocol = models.DateField()
    eudract_number = models.CharField(max_length=40, null=True)
    isrctn_number = models.CharField(max_length=40, null=True)
    sponsor_name = models.CharField(max_length=80, null=True)
    sponsor_contactname = models.CharField(max_length=80, null=True)
    sponsor_address1 = models.CharField(max_length=60, null=True)
    sponsor_address2 = models.CharField(max_length=60, null=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=40, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True)
    sponsor_email = models.EmailField(null=True)
    invoice_name = models.CharField(max_length=80, null=True)
    invoice_contactname = models.CharField(max_length=80, null=True)
    invoice_address1 = models.CharField(max_length=60, null=True)
    invoice_address2 = models.CharField(max_length=60, null=True)
    invoice_zip_code = models.CharField(max_length=10, null=True)
    invoice_city = models.CharField(max_length=40, null=True)
    invoice_phone = models.CharField(max_length=30, null=True)
    invoice_fax = models.CharField(max_length=30, null=True)
    invoice_email = models.EmailField(null=True)
    invoice_uid = models.CharField(max_length=30, null=True) # 24? need to check
    invoice_uid_verified_level1 = models.DateTimeField(null=True) # can be done via EU API
    invoice_uid_verified_level2 = models.DateTimeField(null=True) # can be done manually via Tax Authority, local.
    # TODO: invoice_uid_verified_level2 should also have a field who handled the level2 verification.
    
    # page 2:

    for i in ("2_1_1", "2_1_2", "2_1_2_1", "2_1_2_2", 
              "2_1_3", "2_1_4", "2_1_4_1", "2_1_4_2", 
              "2_1_4_3", "2_1_5", "2_1_6", "2_1_7", 
              "2_1_8", "2_1_9"):
        exec "project_type_%s = models.BooleanField()" % i
    
    specialism = models.TextField(null=True) # choices???
    pharma_checked_substance = models.TextField(null=True)
    pharma_reference_substance = models.TextField(null=True)
    
    medtech_checked_product = models.TextField(null=True)
    medtech_reference_substance = models.TextField(null=True)

    clinical_phase = models.CharField(max_length=10)
    already_voted = models.BooleanField()
    
    subject_count = models.IntegerField()
    subject_minage = models.IntegerField()
    subject_maxage = models.IntegerField()
    subject_noncompetents = models.BooleanField()
    subject_males = models.BooleanField()    
    subject_females = models.BooleanField()
    subject_childbearing = models.BooleanField()
    subject_duration = models.CharField(max_length=20)
    subject_duration_active = models.CharField(max_length=20)
    subject_duration_controls = models.CharField(max_length=20)
    subject_planned_total_duration = models.CharField(max_length=20)

    # page 3:

    substance_registered_in_countries = models.CharField(max_length=300, null=True) # comma seperated 2 letter codes.
    substance_preexisting_clinical_tries = models.NullBooleanField()
    substance_p_c_t_countries = models.CharField(max_length=300, null=True) # comma seperated 2 letter codes.
    substance_p_c_t_phase = models.CharField(max_length=10, null=True)
    substance_p_c_t_period = models.TextField(null=True)
    substance_p_c_t_application_type = models.CharField(max_length=40, null=True)
    substance_p_c_t_gcp_rules = models.NullBooleanField()
    substance_p_c_t_final_report = models.NullBooleanField()

    medtech_product_name = models.CharField(max_length=80, null=True)
    medtech_manufacturer = models.CharField(max_length=80, null=True)
    medtech_certified_for_exact_indications = models.NullBooleanField()
    medtech_certified_for_other_indications = models.NullBooleanField()
    medtech_ce_symbol = models.NullBooleanField()
    medtech_manual_included = models.NullBooleanField()
    medtech_technical_safety_regulations = models.TextField(null=True)
    medtech_technical_safety_regulations = models.TextField(null=True)
    medtech_departure_from_regulations = models.TextField(null=True)

    insurance_name = models.CharField(max_length=60, null=True)
    insurance_address_1 = models.CharField(max_length=80, null=True)
    insurance_phone = models.CharField(max_length=30, null=True)
    insurance_contract_number = models.CharField(max_length=60, null=True)
    insurance_validity = models.CharField(max_length=60, null=True)

    # page 5
    
    additional_therapy_info = models.TextField()

    # page 6

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

    # page 7
    german_statistical_info = models.TextField(null=True)
    german_dataprotection_info = models.TextField(null=True)
    german_aftercare_info = models.TextField(null=True)
    german_payment_info = models.TextField(null=True)
    german_abort_info = models.TextField(null=True)
    german_dataaccess_info = models.TextField(null=True)
    german_financing_info = models.TextField(null=True)
    #     @form_meta(tab=7, paper="7.20")
    #     def form_meta(**kw):
    #         def func(f):
    #             for k, v in kw.items():
    #                 setattr(f, k, v)
    #             return f
    #         return func
            
    german_additional_info = models.TextField(null=True)

    
    # page 8

    for i in range(1, 15):
        exec "study_plan_8_1_%d = models.BooleanField(default=False)" % i

    for i in range(15, 23):
        exec "study_plan_8_1_%d = models.TextField(default='', null=True)" % i

    study_plan_alpha = models.CharField(max_length=40)
    study_plan_power = models.CharField(max_length=40)
    study_plan_statalgorithm = models.CharField(max_length=40)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=40)
    study_plan_dropout_ratio = models.CharField(max_length=40)

    study_plan_8_3_1 = models.BooleanField()
    study_plan_8_3_2 = models.BooleanField()
    study_plan_abort_crit = models.CharField(max_length=40)
    study_plan_planned_statalgorithm = models.CharField(max_length=40)

    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    study_plan_biometric_planning = models.CharField(max_length=120)
    study_plan_statistics_implementation = models.CharField(max_length=120)

    # either anonalgorith or reason or dvr may be set.
    study_plan_dataprotection_reason = models.CharField(max_length=120)
    study_plan_dataprotection_dvr = models.CharField(max_length=12)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True)

    # page 9
    
    submitter_name = models.CharField(max_length=80)
    submitter_organisation = models.CharField(max_length=80)
    submitter_jobtitle = models.CharField(max_length=80)
    submitter_is_coordinator = models.BooleanField()
    submitter_is_main_investigator = models.BooleanField()
    submitter_is_sponsor = models.BooleanField()
    submitter_is_authorized_by_sponsor = models.BooleanField()

    # needs to be nullable.
    submitter_sign_date = models.DateField()

    # page 11
    # wrong class???
    investigator_name = models.CharField(max_length=80)
    investigator_organisation = models.CharField(max_length=80)
    investigator_phone = models.CharField(max_length=30)
    investigator_mobile = models.CharField(max_length=30)
    investigator_fax = models.CharField(max_length=30)
    investigator_email = models.EmailField()
    investigator_jus_practicandi = models.BooleanField()
    investigator_specialist = models.CharField(max_length=80)
    investigator_certified = models.BooleanField()

class Investigator(models.Model):
    submission = models.ForeignKey(SubmissionForm)

    name = models.CharField(max_length=80)
    organisation = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30)
    fax = models.CharField(max_length=30)
    email = models.EmailField()
    jus_practicandi = models.BooleanField()
    specialist = models.CharField(max_length=80)
    certified = models.BooleanField()
    subject_count = models.IntegerField()
    sign_date = models.DateField()

class InvestigatorEmployee(models.Model):
    submission = models.ForeignKey(Investigator)

    sex = models.CharField(max_length=1, choices=[("m", "male"), ("f", "female"), ("?", "")])
    title = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)

class TherapiesApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)

class DiagnosticsApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)


class NonTestedUsedDrugs(models.Model):
    submission = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)

class ParticipatingCenter(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    name = models.CharField(max_length=60)
    address_1 = models.CharField(max_length=60)
    address_2 = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=4)
    
class Amendment(models.Model):
    submissionform = models.ForeignKey(SubmissionForm)
    order = models.IntegerField()
    number = models.CharField(max_length=40)
    date = models.DateField()

class NotificationForm(models.Model):
    def _get_typ(self):
        typ = "???"
        if self.yearly_report:
            typ = "Jahresbericht"
        elif self.final_report:
            typ = "Abschlussbericht"
        elif self.amendment_report:
            typ = "Ergaenzungsreport"
        elif self.SAE_report:
            typ = "SAE Bericht"
        elif self.SUSAR_report:
            typ = "SUSAR Bericht"
        return typ

    typ = property(_get_typ)
    def __str__(self):
        prot = self.notification.submission.sets.get().submissionform.protocol_number
        return u" ".join((self.typ, "EK-343/2009", prot, "vom", self.signed_on or "12.02.2010"))
    # some of these NULLs are obviously wrong, but at least with sqlite
    # south insists on them.
    notification = models.ForeignKey("Notification", null=True, related_name="form")
    submission_form = models.ForeignKey("SubmissionForm", null=True)
    investigator = models.ForeignKey(Investigator, null=True)
    investigator.__doc__ = "set this if this notification is " \
        "specific to a given investigator"
    yearly_report = models.BooleanField(default=False)
    final_report = models.BooleanField(default=False)
    amendment_report = models.BooleanField(default=False)
    SAE_report = models.BooleanField(default=False)
    SUSAR_report = models.BooleanField(default=False)
    # The following should be probably deductible from the submission form
    # and all other tables but currently we are missing those:
    date_of_vote = models.DateField(null=True)
    ek_number = models.CharField(max_length=40, default="")
    
    reason_for_not_started = models.TextField(null=True)
    recruited_subjects = models.IntegerField(null=True)
    finished_subjects = models.IntegerField(null=True)
    aborted_subjects = models.IntegerField(null=True)
    SAE_count = models.IntegerField(null=True)
    SUSAR_count = models.IntegerField(null=True)
    runs_till = models.DateField(null=True)
    finished_on = models.DateField(null=True)
    aborted_on = models.DateField(null=True)
    
    comments = models.TextField(default="")
    
    extension_of_vote = models.BooleanField(default=False)
    signed_on = models.DateField(null=True)

class Checklist(models.Model):
    pass

class SubmissionSet(models.Model):
    submission = models.ForeignKey("Submission", related_name="sets")
    documents = models.ManyToManyField(Document)
    submissionform = models.ForeignKey(SubmissionForm)

class VoteReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Vote(models.Model):
    votereview = models.ForeignKey(VoteReview)
    submissionset = models.ForeignKey(SubmissionSet)
    checklists = models.ManyToManyField(Checklist)
    workflow = models.ForeignKey(Workflow)

class SubmissionReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Submission(models.Model):
    submissionreview = models.ForeignKey(SubmissionReview, null=True)
    vote = models.ForeignKey(Vote, null=True)
    workflow = models.ForeignKey(Workflow, null=True)


class NotificationAnswer(models.Model):
    workflow = models.ForeignKey(Workflow)
 
class Notification(models.Model):
    def __str__(self):
        return str(self.form.get())
    submission = models.ForeignKey(Submission, null=True)
    documents = models.ManyToManyField(Document)
    answer = models.ForeignKey(NotificationAnswer, null=True)
    workflow = models.ForeignKey(Workflow, null=True)

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

