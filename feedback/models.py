from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from tracrpc import tracrpc

# Create your models here.

class Feedback(models.Model):
    FEEDBACK_TYPES=(('i', 'Idea'),('q','Question'),('p', 'Problem'),('l','Praise'))
    feedbacktype = models.CharField(choices=FEEDBACK_TYPES, max_length=1)
    summary = models.CharField(max_length=200) 
    description = models.TextField()
    origin = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name='author', null=True)
    pub_date = models.DateTimeField('date published')
    me_too_votes = models.ManyToManyField(User, null=True, blank=True)
    
    trac_ticket_id = models.IntegerField(null=True)
    
    def _get_tracrpc(self):
        #return tracrpc.TracRpc(settings.FEEDBACK_RPC_CONFIG['username'], settings.FEEDBACK_RPC_CONFIG['password'], settings.FEEDBACK_RPC_CONFIG['proto'], settings.FEEDBACK_RPC_CONFIG['host'], settings.FEEDBACK_RPC_CONFIG['urlpath'])
        return tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
        #return tracrpc.TracRpc('sharing', 'uehkdkDijepo833', 'https', 'ecsdev.ep3.at', '/project/ecs')
    
    def _create_trac_ticket(self):
        tracrpc = self._get_tracrpc()
        #summary = feedback.description because feedback.summary is always empty
        ticket = {'summary': self.description,
                  'description': self.summary,
                  'location': '',#what goes in here? cleaned version of self.origin?
                  'absoluteurl': self.origin,
                  'type': self.get_feedbacktype_display().lower(),
                  'cc': self.user.email,
                  'milestone': settings.FEEDBACK_CONFIG['milestone']}
        #'reporter': self.user.email,
        
        try:
            success, result = tracrpc._create_ticket(summary=self.summary, ticket=ticket, description=self.description)
        except:
            raise
        return success, result


    def save(self, *args, **kwargs):
        #print ""
        #print "saving lala"
        #print ""
        if 'dont_create_ticket' in kwargs and kwargs['dont_create_ticket'] == True:
            super(Feedback, self).save(*args, **kwargs)
        else:
            if settings.FEEDBACK_CONFIG['create_trac_tickets'] == True:
                success, result = self._create_trac_ticket()
                if success:
                    self.trac_ticket_id = result
            super(Feedback, self).save(*args, **kwargs)
        

    def me_too_votes_add(self, user=None):
        if user is None:
            return
        self._update_ticket_cc(user, add=True)
        self.me_too_votes.add(user)
        
    def me_too_votes_remove(self, user=None):
        if user is None:
            return
        
        self._update_ticket_cc(user, add=False)
        self.me_too_votes.remove(user)
    
    def _update_ticket_cc(self, user=None, add=True):
        if user is None:
            return
        
        tracrpc = self._get_tracrpc()
        ticket = tracrpc._get_ticket(self.trac_ticket_id)
        if ticket is None:
            #FIXME ticket could have been deleted, but trac could also jsut be anreachable or its just an rpc protocol error (none is returned)
            #ticket got deleted
            success, result = self._create_trac_ticket()
            if success:
                self.trac_ticket_id = result
                self.save(dont_create_ticket=True)
            ticket = tracrpc._get_ticket(self.trac_ticket_id)
        
        emails = ticket['cc'].split(',')
        in_cc = False
        for email in emails:
            if user.email in email:
                in_cc = True
                if not add:
                    emails.remove(email)
                    
        if add and not in_cc:
            update_ticket = {'cc': "%s,%s" % (ticket['cc'], user.email)}
            comment = ''
            tracrpc._update_ticket(self.trac_ticket_id, update_ticket, action='leave', comment=comment)
        
        if not add and in_cc:
            update_ticket = {'cc':','.join(emails)}
            comment = ''
            tracrpc._update_ticket(self.trac_ticket_id, update_ticket, action='leave', comment=comment)
    
    
    
    
    
    
    
    
    
        
    