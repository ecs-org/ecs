from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='ecs_profile')

    external_review = models.BooleanField(default=False)
    board_member = models.BooleanField(default=False)
    executive_board_member = models.BooleanField(default=False)
    thesis_review = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'core'
    

def _post_user_save(sender, **kwargs):
    if kwargs['created'] and not kwargs.get('raw'): # 'raw' is passed during fixture loading
        UserProfile.objects.create(user=kwargs['instance'])
    
post_save.connect(_post_user_save, sender=User)
   