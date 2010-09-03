import datetime
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='ecs_profile')
    gender = models.CharField(max_length=1, choices=(('w', 'Frau'), ('m', 'Herr')))
    last_password_change = models.DateTimeField(default=datetime.datetime.now)
    approved_by_office = models.BooleanField(default=False)

    external_review = models.BooleanField(default=False)
    board_member = models.BooleanField(default=False)
    executive_board_member = models.BooleanField(default=False)
    thesis_review = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)

    session_key = models.CharField(max_length=40, null=True)
    
    def __unicode__(self):
        return unicode(self.user.username)
    

def _post_user_save(sender, **kwargs):
    # FIXME: 'raw' is passed during fixture loading, but that's an undocumented feature - see django bug #13299
    if kwargs['created'] and not kwargs.get('raw'):
        UserProfile.objects.create(user=kwargs['instance'])
    
post_save.connect(_post_user_save, sender=User)
   
