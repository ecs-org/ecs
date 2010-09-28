import datetime
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from ecs.core.models.submissions import SubmissionForm, Investigator

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='ecs_profile')
    gender = models.CharField(max_length=1, choices=(('w', 'Frau'), ('m', 'Herr')))
    last_password_change = models.DateTimeField(default=datetime.datetime.now)
    approved_by_office = models.BooleanField(default=False)

    external_review = models.BooleanField(default=False)
    board_member = models.BooleanField(default=False)
    executive_board_member = models.BooleanField(default=False)
    thesis_review = models.BooleanField(default=False)
    insurance_review = models.BooleanField(default=False)
    expedited_review = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)

    session_key = models.CharField(max_length=40, null=True)
    
    def __unicode__(self):
        return unicode(self.user.username)
    
    def attach_to_submissions(self):
        sf_by_submitter_email = SubmissionForm.objects.filter(submitter_email=self.user.email)
        for sf in sf_by_submitter_email:
            sf.submitter = self.user.email
            sf.save()
            
        sf_by_sponsor_email = SubmissionForm.objects.filter(sponsor_email=self.user.email)
        for sf in sf_by_sponsor_email:
            sf.sponsor = self.user.email
            sf.save()
            
        investigator_by_email = Investigator.objects.filter(email=self.user.email)
        
        for inv in investigator_by_email:
            inv.user = self.user.email
            inv.save()
            
def _post_user_save(sender, **kwargs):
    # XXX: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299 (FMD1)
    if kwargs['created'] and not kwargs.get('raw'):
        UserProfile.objects.create(user=kwargs['instance'])
    
post_save.connect(_post_user_save, sender=User)
   
