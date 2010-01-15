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
    absent = models.Boolean()

    # FileField might be enough, OTOH we'll have really many files.
    # So a more clever way of storage might be useful.
    def open(self, mode):
        """returns a binary file object for reading/writing of the document depending upon mode"""
        assert False, "not yet implemented"



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

class SubmissionForm(models.Model):
    project_title = models.CharField(max_length=120)
    protocol_number = models.CharField(max_length=40)
    date_of_protocol = models.DateField()
    eudract_number = models.CharField(max_length=40)
    isrctn_number = models.CharField(max_length=40)
    sponsor_name = models.CharField(max_length=80)
    sponsor_address1 = models.CharField(max_length=60)
    sponsor_address2 = models.CharField(max_length=60)
    sponsor_zip_code = models.CharField(max_length=10)
    sponsor_city = models.CharField(max_length=40)
    sponsor_phone = models.CharField(max_length=30)
    sponsor_fax = models.CharField(max_length=30)
    sponsor_email = models.EmailField()
    invoice_name = models.CharField(max_length=80)
    invoice_address1 = models.CharField(max_length=60)
    invoice_address2 = models.CharField(max_length=60)
    invoice_zip_code = models.CharField(max_length=10)
    invoice_city = models.CharField(max_length=40)
    invoice_phone = models.CharField(max_length=30)
    invoice_fax = models.CharField(max_length=30)
    invoice_email = models.EmailField()
    invoice_uid = models.CharField(max_length=30) # 24? need to check
    invoice_uid_verified_level1 = models.DateTimeField(null=True) # can be done via EU API
    invoice_uid_verified_level2 = models.DateTimeField(null=True) # can be done manually via Tax Authority, local.
    
    # page 2:

    for i in ("2_1_1", "2_1_2", "2_1_2_1", "2_1_2_2", 
              "2_1_3", "2_1_4", "2_1_4_1", "2_1_4_2", 
              "2_1_4_3", "2_1_5", "2_1_6", "2_1_7", 
              "2_1_8", "2_1_9"):
        exec "project_type_%s = models.BooleanField()" % i
    
    specialism = models.CharField(max_length=80) # choices???
    pharma_checked_substance = models.CharField(max_length=80)
    pharma_reference_substance = models.CharField(max_length=80)
    
    medtech_checked_product = models.CharField(max_length=80)
    medtech_reference_substance = models.CharField(max_length=80)

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

    substance_registered_in_countries = models.CharField(max_length=300) # comma seperated 2 letter codes.
    substance_preexisting_clinical_tries = models.BooleanField()
    substance_p_c_t_countries = models.CharField(max_length=300) # comma seperated 2 letter codes.
    substance_p_c_t_phase = models.CharField(max_length=10)
    substance_p_c_t_period = models.CharField(max_length=40)
    substance_p_c_t_application_type = models.CharField(max_length=40)
    substance_p_c_t_gcp_rules = models.BooleanField()
    substance_p_c_t_final_report = models.BooleanField()

    medtech_product_name = models.CharField(max_length=80)
    medtech_manufacturer = models.CharField(max_length=80)
    medtech_certified_for_exact_indications = models.BooleanField()
    medtech_certified_for_other_indications = models.BooleanField()
    medtech_ce_symbol = models.BooleanField()
    medtech_manual_included = models.BooleanField()
    medtech_technical_safety_regulations = models.CharField(max_length=120)
    medtech_technical_safety_regulations = models.CharField(max_length=120)
    medtech_departure_from_regulations = models.CharField(max_length=120)

    insurance_name = models.CharField(max_length=60)
    insurance_address_1 = models.CharField(max_length=80)
    insurance_phone = models.CharField(max_length=30)
    insurance_contract_number = models.CharField(max_length=60)
    insurance_validity = models.CharField(max_length=60)

    # page 5
    
    additional_therapy_info = models.TextField()

    # page 6

    german_project_title = models.CharField(max_length=120)
    german_summary = models.CharField(max_length=120)
    german_preclinical_results = models.CharField(max_length=120)
    german_primary_hypothesis = models.CharField(max_length=120)
    german_inclusion_exclusion_crit = models.CharField(max_length=120)
    german_ethical_info = models.CharField(max_length=120)
    german_protected_subjects_info = models.CharField(max_length=120)
    german_recruitment_info = models.CharField(max_length=120)
    german_consent_info = models.CharField(max_length=120)
    german_risks_info = models.CharField(max_length=120)
    german_benefits_info = models.CharField(max_length=120)
    german_relationship_info = models.CharField(max_length=120)
    german_concurrent_study_info = models.CharField(max_length=120)
    german_sideeffects_info = models.CharField(max_length=120)

    # page 7
    
    german_statistical_info = models.CharField(max_length=120)
    german_dataprotection_info = models.CharField(max_length=120)
    german_aftercare_info = models.CharField(max_length=120)
    german_payment_info = models.CharField(max_length=120)
    german_abort_info = models.CharField(max_length=120)
    german_dataaccess_info = models.CharField(max_length=120)
    german_financing_info = models.CharField(max_length=120)
    german_additional_info = models.CharField(max_length=120)

    # page 8

    for i in range(1, 15):
        exec "study_plan_8_1_%d = models.BooleanField()" % i

    for i in range(15, 22):
        exec "study_plan_8_1_%d = models.CharField(max_length=80)" % i

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
    study_plan_dataprotection_anonalgoritm = models.CharField(max_length=12)

    # page 9
    
    submitter_name = models.CharField(max_length=80)
    submitter_organisation = models.CharField(max_length=80)
    submitter_jobtitle = models.CharField(max_length=80)
    submitter_is_coordinator = models.BooleanField()
    submitter_is_main_investigator = models.BooleanField()
    submitter_is_sponsor = models.BooleanField()
    submitter_is_authorized_by_sponsor = models.BooleanField()

    submitter_sign_date = models.DateField()

    # page 11

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

    sex = models.CharField(max_length=1, choices=["m", "f", "?"])
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
    pass

class Checklist(models.Model):
    pass

class SubmissionSet(models.Model):
    submission = models.ForeignKey("Submission", related_name="sets")
    documents = models.ManyToManyField(Document)
    submissionform = models.ForeignKey(SubmissionForm)

class NotificationSet(models.Model):
    documents = models.ManyToManyField(Document)
    notificationform = models.ForeignKey(NotificationForm)

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
    submissionreview = models.ForeignKey(SubmissionReview)
    vote = models.ForeignKey(Vote)
    workflow = models.ForeignKey(Workflow)


class NotificationAnswer(models.Model):
    workflow = models.ForeignKey(Workflow)
 
class Notification(models.Model):
    submission = models.ForeignKey(Submission)
    notificationset = models.ForeignKey(NotificationSet)
    answer = models.ForeignKey(NotificationAnswer)
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

