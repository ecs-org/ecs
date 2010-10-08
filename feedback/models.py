from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from ecs.utils import tracrpc

# Create your models here.

class Feedback(models.Model):
    FEEDBACK_TYPES=(('i', 'Idea'),('q','Question'),('p', 'Problem'),('l','Praise'))
    ftdict = dict(FEEDBACK_TYPES)
    tracrpc = tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
    rpc_query_base = "order=id&col=id&col=summary&col=status&col=type&col=priority&col=milestone&col=component"
    
    def __init__(self, *args, **kwargs):
        self.ftdict = dict(self.FEEDBACK_TYPES)
        feedbacktype = ''
        summary = '' 
        description = ''
        origin = ''
        user = ''
        pub_date = ''
        me_too_votes = 0
        me_too_emails = []
        creator_email = ''
        trac_ticket_id = 0
        super(Feedback, self).__init__(*args, **kwargs)
        
    @classmethod
    def _get_tracrpc(cls):
        #return tracrpc.TracRpc(settings.FEEDBACK_RPC_CONFIG['username'], settings.FEEDBACK_RPC_CONFIG['password'], settings.FEEDBACK_RPC_CONFIG['proto'], settings.FEEDBACK_RPC_CONFIG['host'], settings.FEEDBACK_RPC_CONFIG['urlpath'])
        #return tracrpc.TracRpc.from_dict(settings.FEEDBACK_CONFIG['RPC_CONFIG'])
        return cls.tracrpc
        #return tracrpc.TracRpc('sharing', 'uehkdkDijepo833', 'https', 'ecsdev.ep3.at', '/project/ecs')
    
    
    def _create_trac_ticket(self):
        tracrpc = self._get_tracrpc()
        #summary = feedback.description because feedback.summary is always empty
        #summary = description is on purpose
        ticket = {'summary': self.description,
                  'description': self.summary,
                  'location': '',#what goes in here? cleaned version of self.origin?
                  'absoluteurl': self.origin,
                  'type': self.feedbacktype,
                  'cc': self.creator_email,
                  'ecsfeedback_creator': self.creator_email,
                  'milestone': settings.FEEDBACK_CONFIG['milestone']}
        
        try:        
            success, result = tracrpc._create_ticket(summary=self.summary, ticket=ticket, description=self.description)
        except:
            raise
        return success, result

    @classmethod
    def get(cls, tid):
        ticket = cls.tracrpc._get_ticket(tid)
        if ticket is None:
            return None
        ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
        return cls.init_from_dict(ticket)
    
    @classmethod
    def init_from_dict(cls, ticket):
        fb = Feedback()
        fb.trac_ticket_id = ticket['id'] if ticket.has_key('id') else None
        fb.feedbacktype = ticket['type']
        #summary = description is on purpose
        fb.summary = ticket['description'] 
        fb.description = ticket['summary']
        fb.origin = ticket['absoluteurl']
        #fb.user = user wont work this way - user lookup via email is not unique and waste of time 
        fb.pub_date = ''
        fb.me_too_emails_string = ticket['cc']
        fb.me_too_emails = cls.comma_string_2_list(ticket['cc'])
        fb.me_too_votes = len(fb.me_too_emails)
        fb.creator_email = ticket['ecsfeedback_creator']
        return fb
    
    @classmethod
    def query(cls, limit_from=0, limit_to=9999, feedbacktype=None, origin=None):
        fb_list = []
        query = cls.rpc_query_base
        if feedbacktype is not None:
            query += "&type=%s" % cls.ftdict[feedbacktype].lower()
        if origin is not None:
            query += "&absoluteurl=%s" % origin
    
        ticket_ids = cls.tracrpc._safe_rpc(cls.tracrpc.jsonrpc.ticket.query, query)
        if ticket_ids is None:
            return 0,[]
        
        overall_count = len(ticket_ids)
        mc = cls.tracrpc.multicall()
        for tid in ticket_ids[limit_from:limit_to]:
            mc.ticket.get(tid)
        mc_results = cls.tracrpc._safe_rpc(mc)
        
        if mc_results is None:
            return 0,[]
        
        ticket_count = len(mc_results.results['result'])
        for result in mc_results.results['result']:
            ticket = cls.tracrpc._get_ticket_from_rawticket(result['result'])
            ticket = tracrpc.TracRpc.pad_ticket_w_emptystrings(ticket, settings.FEEDBACK_CONFIG['ticketfieldnames'])
            fb_list.append(cls.init_from_dict(ticket))
        return overall_count, fb_list
    
    @staticmethod
    def comma_string_2_list(commastring):
        oldlist = commastring.split(',')
        nlist = []
        for item in oldlist:
            if item.strip() != '':
                nlist.append(item.strip())
                
        return nlist
        
    
    def save(self, *args, **kwargs):
        if settings.FEEDBACK_CONFIG['create_trac_tickets'] == True:
            success, result = self._create_trac_ticket()
            if success:
                self.trac_ticket_id = result
        
        if settings.FEEDBACK_CONFIG['store_in_db']:
            super(Feedback, self).save(*args, **kwargs)
        

    def me_too_votes_add(self, user=None):
        if user is None:
            return
        if settings.FEEDBACK_CONFIG['create_trac_tickets'] == True:
            self._update_ticket_cc(user, add=True)
        
    def me_too_votes_remove(self, user=None):
        if user is None:
            return
        if settings.FEEDBACK_CONFIG['create_trac_tickets'] == True:
            self._update_ticket_cc(user, add=False)
    
    def _update_ticket_cc(self, user=None, add=True):
        if user is None:
            return
        in_cc = False
        for email in self.me_too_emails:
            if user.email in email:
                in_cc = True
                if not add:
                    self.me_too_emails.remove(email)
            
        if add and not in_cc:
            update_ticket = {'cc': "%s,%s" % (self.me_too_emails_string, user.email)}
            comment = ''
            self.tracrpc._update_ticket(self.trac_ticket_id, update_ticket, action='leave', comment=comment)
        
        if not add and in_cc:
            update_ticket = {'cc':','.join(self.me_too_emails)}
            comment = ''
            self.tracrpc._update_ticket(self.trac_ticket_id, update_ticket, action='leave', comment=comment)
    
    
    
    
    
    
    
    
    
        
    
