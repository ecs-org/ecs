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

class TherapiesApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    dosage = models.CharField(max_length=30)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)

class DiagnosticsApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    dosage = models.CharField(max_length=30)
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

