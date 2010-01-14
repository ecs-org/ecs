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
    pass

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

