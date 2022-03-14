import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class EthicsCommission(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=120)
    vote_receiver = models.EmailField(null=True, blank=True)
    
    def __str__(self):
        return self.name
        
    @property
    def system(self):
        return self.uuid == uuid.UUID(settings.ETHICS_COMMISSION_UUID)

class MedicalCategory(models.Model):
    name = models.CharField(max_length=60)
    abbrev = models.CharField(max_length=12, unique=True)
    is_disabled = models.BooleanField(default=False)
    users = models.ManyToManyField(User, related_name='medical_categories')

    def __str__(self):
        return '%s (%s)' % (self.name, self.abbrev)

class AdvancedSettings(models.Model):
    default_contact = models.ForeignKey(User)
    display_notifications_in_protocol = models.BooleanField(default=False)
    display_biased_in_amendment_answer_pdf = models.BooleanField(default=True)
    require_internal_vote_review = models.BooleanField(default=False)

    # custom logos
    logo = models.BinaryField(null=True)
    logo_mimetype = models.CharField(max_length=100, null=True)
    print_logo = models.BinaryField(null=True)
    print_logo_mimetype = models.CharField(max_length=100, null=True)

    # additional vote text
    vote1_extra = models.TextField(null=True, blank=True)
    vote2_extra = models.TextField(null=True, blank=True)
    vote3a_extra = models.TextField(null=True, blank=True)
    vote3b_extra = models.TextField(null=True, blank=True)
    vote4_extra = models.TextField(null=True, blank=True)
    vote5_extra = models.TextField(null=True, blank=True)
    vote_pdf_extra = models.TextField(null=True, blank=True)

    # EC information
    address = models.TextField(null=True)
    meeting_address = models.TextField(null=True)
    contact_email = models.EmailField(null=True)
    contact_url = models.URLField(null=True)
    member_list_url = models.URLField(null=True)
    signature_block = models.TextField(null=True)
