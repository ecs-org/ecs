# -*- coding: utf-8 -*-
"""
a class for interfacing with Trac via jsonrpc 
"""

import os, sys, tempfile, datetime, subprocess, re
from pprint import pprint
import urllib2, urllib


import json_hack
import jsonrpclib
import codecs

#urllib2 madness fix:
import base64

    
jsonrpclib.config.use_jsonclass = True
jsonrpclib.config.classes.add(datetime.datetime)

def get_editor():
    '''
    returns name of editor the user wants, or None if neither EDITOR environment variable is set nor we have a platform default
    (the result should be called via shell=True, because we need the shell to evaluate the path)
    '''
    if os.getenv("EDITOR", None) is None:        
        if sys.platform == "win32":
            editor = "notepad"
        elif sys.platform in ['darwin', 'linux2']:
            editor = "vi"
        else:
            return None
    else:
        editor = os.getenv("EDITOR")
    return editor

def _get_agilo_links(raw=False, testtrac=False):
    ''' get it somewhere else
usage: calls getlinks.sh as ecsdev@ecsdev.ep3.at
getlinks makes a select * from ecs.agilo_link from database ecsdev as user ecsdev, and pipes its output to stdout
result is a list with source|dest links, to be parsed

this is to be called to construct links from agilo to make the "perfect" validation company documents ,-)

    '''
    from fabric.api import run, env, settings, hide
    env.host_string = 'ecsdev@ecsdev.ep3.at'
    with settings(hide('stdout')):
        #TODO hide output of fabric executing the script
        #saveout = sys.stdout
        #sys.stdout = ''
        if testtrac:
            result = run("~/getlinks_ekreqtest.sh")
        else:
            result = run("~/getlinks.sh")
        #sys.stdout = saveout
    if raw:
        return result
    else:
        return _parse_agilo_links(result)

def _parse_agilo_links(text):
    ''' '''
    
    ids = []
    lines = text.splitlines()
    ids = [int(id) for line in text.splitlines() for id in line.split('|')]
    links=[]            #list of ticketlinkstuples, (src,dst)
    linkd = {}          #dict of linksources:[targets]
    reverselinkd = {}   #dict of linktargets:[sources]
    for line in lines:
        src,dst = line.split("|")
        src = int(src)
        dst = int(dst)
        links.append((src,dst))
        if not linkd.has_key(src):
            linkd[src] = [dst]
        else:
            linkd[src].append(dst)
        if not reverselinkd.has_key(dst):
            reverselinkd[dst] = [src]
        else:
            reverselinkd[dst].append(src)
    
    return ids,links,linkd,reverselinkd

 

class HttpBot():
    ''' '''
    
    tracproto = None
    trachost = None
    tracpath = None
    #tracurl = "https://ecsdev.ep3.at/project/ekreq"
    tracurl = "%s://%s%s" % (tracproto, trachost, tracpath)
    ticketlinkurl = tracurl +"/links"
    
    username=None
    password=None
    
    opener = None
    cookie_handler = None
    auth_handler = None
    form_token = None
    
    
    authstring = None
    
    
    def __init__(self, user=None, password=None, protocol=None, hostname=None, urlpath=None, realm=None):
        '''Constructor'''
        
        if not user or not password:
            print "error. No user or password for httpbot supplied."
            return None
        if not protocol or not hostname or not urlpath:
            print "error. no protocol, or hostname or urlpath given."
            return None
        if not realm:
            print "Warning. no realm specified. using ''"
            realm = ''
        
        self.username = user #fuckup
        self.password = password
        self.tracproto = protocol
        self.trachost = hostname
        self.tracpath = urlpath
        self.tracurl = "%s://%s%s" % (self.tracproto, self.trachost, self.tracpath)
        self.ticketlinkurl = self.tracurl +"/links"
        
        self.auth_handler = urllib2.HTTPBasicAuthHandler()
        self.auth_handler.add_password(realm=realm,
                                  uri=self.tracurl,
                                  user=self.username,
                                  passwd=self.password)
        self.cookie_handler = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(self.auth_handler, self.cookie_handler)
        #self.opener.addheaders = [('User-agent', 'frankenzilla/1.0')] #Mozilla/5.0
        urllib2.install_opener(self.opener)
        
        self.authstring = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        
        request = urllib2.Request(self.tracurl)
        request.add_header("Authorization", "Basic %s" % self.authstring)
        response = self.opener.open(request)
        
        cj = self.cookie_handler.cookiejar
        self.form_token = None
        for c in cj:
            if c.name == 'trac_form_token':
                self.form_token = c.value
    
    
    def _try_vanilla_request_for_form_token(self):
        print "doing vanilla request"
        request = urllib2.Request(self.tracurl)
        request.add_header("Authorization", "Basic %s" % self.authstring)
        response = self.opener.open(request)
        cj = self.cookie_handler.cookiejar
        oldtoken = self.form_token
        for c in cj:
            if c.name == 'trac_form_token':
                self.form_token = c.value
        if oldtoken != self.form_token:
            print "form_token changed!!"
        
    def _update_form_token(self):
        cj = self.cookie_handler.cookiejar
        self.form_token = None
        for c in cj:
            if c.name == 'trac_form_token':
                self.form_token = c.value
        #print "formtoken updated:",self.form_token
        
    def create_ticket_link(self, srcid, destid):
        self._ticket_link(srcid, destid, create=True)
    
    def delete_ticket_link(self, srcid, destid):
        self._ticket_link(srcid, destid, create=False)
        
    def _ticket_link(self, srcid, destid, create=True, retry=False):
        if create:
            cmd = 'create link'
        else:
            cmd = 'delete link'
        data = urllib.urlencode([('url_orig', '%s/ticket/%d?pane=edit' % (self.tracpath, srcid)),
        ('__FORM_TOKEN', self.form_token),
        ('src', srcid),
        ('dest', destid),
        ('autocomplete_parameter', ''),
        ('cmd', cmd)])
        print "sending '%s' request" % (cmd)
        try:
            request = urllib2.Request(self.ticketlinkurl, data)
            request.add_header("Authorization", "Basic %s" % self.authstring)
            response = self.opener.open(request)
            #response = self.opener.open(self.ticketlinkurl, data)
        except urllib2.HTTPError, e: #, Exception
            if e.getcode() == 500:
                print "something wrent wrong and produced a http error 500 while linking ticket %s with %s (src, dst)" % (srcid, destid)
            elif e.getcode() == 401 and e.msg == 'basic auth failed' and retry == False:
                print "basic auth failed. retrying"
                #self._try_vanilla_request_for_form_token()
                self._ticket_link(srcid, destid, create=create, retry=True)
            elif e.getcode() == 401 and e.msg == 'basic auth failed' and retry == True:
                print "basic auth failed twice! giving up"
            else:
                print "unexpected error:"
                print  sys.exc_info()[0]
                print  sys.exc_info()
                pprint(e.__dict__)
                pprint(e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
        
        self._update_form_token()
    
    
class Agilolinks():
    '''a class that holds all ticket links in agilo trac'''
    
    fetched_once = False
    testtrac=False
    ids = None
    links = None
    linkdict = None
    reverselinkdict = None
    
    def __init__(self, testtrac=False):
        self.testtrac = testtrac
    
    def updatecache(self):
        self.ids, self.links, self.linkdict, self.reverselinkdict = _get_agilo_links(raw=False, testtrac=self.testtrac)
        self.fetched_once = True
        
    def get_ticket_childs(self, tid):
        if not self.fetched_once:
            self.updatecache()
        if self.linkdict.has_key(tid):
            return self.linkdict[tid]
        else:
            return []
        
    def get_ticket_parents(self, tid):
        if not self.fetched_once:
            self.updatecache()
        if self.reverselinkdict.has_key(tid):
            return self.reverselinkdict[tid]
        else:
            return []
    
class TracRpc():
    '''
    makes the communication with Trac
    '''
    jsonrpc = None
    _url = None
    debugmode = False
    link_cache = None
    httpbot = None
    validclonetypes = ['task','story','requirement','bug']
    
    def __init__(self, username, password, protocol, hostname, urlpath, debug=False, httprealm=None):
        '''
        example: TracRpc('user', 'password', 'https', 'ecsdev.ep3.at', '/project/ecs')
        '''
        C_TRAC_AUTH_JSON = "login/jsonrpc"
        self._url = '%s://%s:%s@%s%s/%s' % (protocol, username, password, hostname,
                                      urlpath, C_TRAC_AUTH_JSON)
        self.jsonrpc = jsonrpclib.Server(self._url)
        self.debugmode = debug
        self.link_cache = Agilolinks(testtrac = debug)
        self.httpbot = HttpBot(user=username, password=password, protocol=protocol, hostname=hostname, urlpath=urlpath, realm=httprealm)
        
    #see http://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
    @classmethod
    def from_dict(cls, config_dict):
        return cls(config_dict['username'], config_dict['password'], config_dict['proto'], config_dict['host'], config_dict['urlpath'])
    
    @staticmethod
    def _safe_rpc(func, *args, **kwargs):
        '''
        wrapper function for any rpc call
        '''
        try:
            result = func(*args, **kwargs)
        except jsonrpclib.ProtocolError as (strerror):
            print "Json RPC ProtocolError: %s" % strerror
            return None
        return result
    
    def multicall(self):
        return jsonrpclib.MultiCall_agilo(self.jsonrpc)

    @staticmethod
    def _ticket2text(ticket):
        '''
        return ticket dict as string with newlines
        '''
        return "%s%s%s%s%s" % (ticket['summary'], os.linesep, os.linesep,
                               ticket['description'], os.linesep)
    
    @staticmethod
    def _text2ticket(text):
        '''
        convert text into a simple ticket dict
        '''
        ticket = {}
        lines = text.splitlines()
        ticket['summary'] = lines[0] if len(lines) > 0 else None
        if len(lines) > 1:
            descr_begin = 1 if lines[1] != "" else 2
            ticket['description'] = os.linesep.join(lines[descr_begin:])
        else:
            ticket['description'] = None
        ticket['remaining_time'] = None
        ticket['type'] = None
        return ticket
    
    @staticmethod
    def _smartertext2ticket(text):
        ''' '''
        
        nl = u'\n'
        ticket={}
        lines = text.splitlines()
        #ticket['summary'] = lines[0] if len(lines) > 0 else None
        #ticket['milestone'] = lines[1].replace('Milestone=', '')
        #ticket['priority'] = lines[2].replace('Priority=', '')
        #ticket['description'] = nl.join(lines[4:len(lines)])
        
        ticket['summary'] = lines[0] if len(lines) > 0 else None
        i=0
        for line in lines:
            if re.search('^Milestone=', line) != None:
                ticket['milestone'] = re.sub('^Milestone=', '', line)
            if re.search('^Priority=', line) != None:
                tmp = re.sub('^Priority=', '', line)
                if tmp == 'None':
                    ticket['priority'] = None
                else:
                    ticket['priority'] = tmp
            if re.search('^Childlinks=', line) != None:
                tmp = re.sub('^Childlinks=', '', line)
                tmp = tmp.split(',')
                tmpclinks = []
                for link in tmp:
                    if link.strip() != '':
                        try:
                            tmpclinks.append(int(link.strip()))
                        except ValueError:
                            print "malformed id for linking. ignoring."
                ticket['childlinks'] = tmpclinks
            if re.search('^Parentlinks=', line) != None:
                tmp = re.sub('^Parentlinks=', '', line)
                tmp = tmp.split(',')
                tmpplinks = []
                for link in tmp:
                    if link.strip() != '':
                        try:
                            tmpplinks.append(int(link.strip()))
                        except ValueError:
                            print "malformed id for linking. ignoring."
                ticket['parentlinks'] = tmpplinks
            if line == '---description---':
                ticket['description'] = nl.join(lines[i+1:len(lines)])
            i+= 1
        return ticket
        
    
    @staticmethod
    def _smarterticket2text(ticket):
        '''
        return ticket dict as string with newlines
        '''
        descr = ticket['description'].replace(u'\r\n', u'\n')
        summary = ticket['summary']
        nl = u'\n'
        return "%s%sMilestone=%s%sChildlinks=%s%sParentlinks=%s%sPriority=%s%s---description---%s%s%s" % (summary, nl, ticket['milestone'], nl, ticket['childlinks'], nl, ticket['parentlinks'], nl, ticket['priority'], nl, nl, descr, nl)
    
    @staticmethod
    def _minimize_ticket(ticket):
        '''
        remove fields with value None from dict
        '''
        newdict = {}
        for key, value in ticket.iteritems():
            if value is not None:
                newdict[key] = value
        return newdict
    
    @staticmethod
    def pad_ticket_w_emptystrings(ticket, fieldnames):
        '''
        returns new dict with fieldnames set to None if they dont exist in ticket
        '''
        new_ticket = {}
        for key,val in ticket.iteritems():
            new_ticket[key] = val if val is not None else ''
        for name in fieldnames:
            new_ticket[name] = ticket[name] if ticket.has_key(name) and ticket[name] is not None else ''
        
        return new_ticket

    def _get_field(self, rawticket, fieldname):
            '''
            return field value or None out of the list returned by rpc call
            '''
            return rawticket[3][fieldname] if rawticket[3].has_key(fieldname) else None
    
    def _get_ticket(self, tid, getlinks=False):
        '''
        fetches a ticket and return simple dict w/ ticket contents
        '''
        rawticket = self._safe_rpc(self.jsonrpc.ticket.get, tid)
        if not rawticket:
            return None
        ticket = self._get_ticket_from_rawticket(rawticket)
        if getlinks:
            links = self.get_ticket_links(tid)
            ticket['children'] = links['children']
            ticket['parents'] = links['parents']
        return ticket
    
    def _get_ticket_changelog(self, tid):
        '''
        fetches changelog of a ticket
        '''
        changelog = self._safe_rpc(self.jsonrpc.ticket.changeLog, tid)
        if not changelog:
            return None
        return changelog
    
    def _get_ticket_from_rawticket(self, rawticket):
        if not rawticket:
            return None
        else:
            ticket = {}
            ticket['id'] = rawticket[0]
            ticket['summary'] = self._get_field(rawticket, 'summary')
            ticket['description'] = self._get_field(rawticket, 'description')
            ticket['remaining_time'] = self._get_field(rawticket, 'remaining_time')
            ticket['type'] = self._get_field(rawticket, 'type')
            ticket['cc'] = self._get_field(rawticket, 'cc')
            ticket['location'] = self._get_field(rawticket, 'location')
            ticket['absoluteurl'] = self._get_field(rawticket, 'absoluteurl')
            ticket['ecsfeedback_creator'] = self._get_field(rawticket, 'ecsfeedback_creator')
            ticket['milestone'] = self._get_field(rawticket, 'milestone')
            ticket['priority'] = self._get_field(rawticket, 'priority')
            ticket['component'] = self._get_field(rawticket, 'component')
            ticket['status'] = self._get_field(rawticket, 'status')
            ticket['rd_points'] = self._get_field(rawticket, 'rd_points')
            ticket['resolution'] = self._get_field(rawticket, 'resolution')
            ticket['owner'] = self._get_field(rawticket, 'owner')
            ticket['severity'] = self._get_field(rawticket, 'severity')
            ticket['sprint'] = self._get_field(rawticket, 'sprint')
            return ticket
        
    
    def _update_ticket(self, tid, ticket, action=None, comment=None):
        '''
        update any field in a ticket
        '''
        if comment is None:
            comment = ""
        if action is None: 
            action = "leave"
        ticket['action'] = action
        ticket = self._minimize_ticket(ticket)
        
        result = self._safe_rpc(self.jsonrpc.ticket.update, tid, comment, ticket)
        # fixme parse update_result for errors,
        # and return False and error text or whatever)
        return True, ""
    
    def _create_ticket(self, summary, ticket, description='', verbose=False):
        #ticket.create(string summary, string description, struct attributes={}
        result = self._safe_rpc(self.jsonrpc.ticket.create, summary, description, ticket)
        if type(result) == int:
            return True, result
        else:
            return False, result
    
    def create_ticket(self, summary=None, description=None, verbose=False):
        if summary is None:
            sys.stdout.write("summary: ")
            summary = raw_input()
        if description is None:
            sys.stdout.write("description: ")
            description = raw_input()
        
        if summary == '':
            print "a ticket must at least have a summary"
            return
        ticket = {'sprint': 'Sysadmin 8',
        'type': 'task'}
        #'milestone': 'Milestone 8'
        #'remaining_time': '20'
        #'priority': 'important'
        
        success, result = self._create_ticket(summary, ticket, description, verbose)
        if success:
            print "created ticket %d" % result
            return result
        else:
            print "error creating ticket:"
            print result
            return False
    
    def clone_ticket(self, tid=None, clonetype=None, linkcloneasparent=False, linkcloneaschild=False):
        '''clones ticket tid as ticket of type type and optionally links it as  parent or child to source/original ticket'''
        if not tid:
            print "no ticket supplied. returning"
            return None
        ticket = self._get_ticket(tid, getlinks=True)
        if not ticket:
            print "no ticket with id %s. returning." % tid
            return None
        if len(ticket['parents']) > 0:
            print "warning! ticket %s has parents! this relation will not be cloned!" % tid
            confirm = raw_input("continue?(y/n)")
            if confirm.lower() != 'y':
                print "cloning of ticket %s aborted." % tid
                return
        if len(ticket['children']) > 0:
            print "warning! ticket %s has children! this relation will not be cloned! children aswell won't be cloned."
            confirm = raw_input("continue?(y/n)")
            if confirm.lower() != 'y':
                print "cloning of ticket %s aborted." % tid
                return
        
        if ticket['type'] == '' or ticket['type'] == None:
            print "ticket %s has no type! returning." % ticket['id']
            return None
        if clonetype not in self.validclonetypes:
            print "type '%s' is not a valid type to clone 'into'" % clonetype
            return None
        
        cloneticket = ticket
        cloneticket['type'] = clonetype
        success, result = self._create_ticket(cloneticket['summary'], cloneticket, cloneticket['description'])
        if success:
            print "ticket %s created as clone of %s" % (result, tid)
            if linkcloneasparent:
                self.link_tickets(int(result), [tid], deletenonlistedtargets=False)
            if linkcloneaschild:
                self.link_tickets(tid, [int(result)], deletenonlistedtargets=False)
            return result
        else:
            print "cloning of %s as story failed" % (taskid)
            return None
        
        
    def clone_storyfromtask_andlinkthem(self, taskid=None):
        '''takes a ticket w type=task and creates a story with same content as task and links the task to the story'''
        if not taskid:
            print "no task ticket supplied. returning"
            return None
        taskticket = self._get_ticket(taskid, getlinks=True)
        if not taskticket:
            print "no ticket with id %s. returning." % taskid
            return None
        if len(taskticket['parents']) > 0:
            print "this task already has parentlink(s)! returning"
            return None
    
        if taskticket.has_key("type"):
            if taskticket['type'] != 'task':
                print "ticket %s is not of type task! returning." % ticket['id']
                return None
        else:
            print "ticket %s has no type! returning." % ticket['id']
            return None
        
        story = taskticket
        story['type'] = 'story'
        success, result = self._create_ticket(story['summary'], story, story['description'])
        if success:
            print "ticket %s created as clone of %s" % (result, taskid)
            self.link_tickets(int(result), [taskid], deletenonlistedtargets=False)
            return result
        else:
            print "cloning of %s as story failed" % (taskid)
            return None
    
    def show_ticket(self, tid, verbose=False):
        '''
        show simple or verbose ticket representation to user
        '''
        ticket = self._get_ticket(tid)
        if not ticket:
            print "could not fetch ticket %d" % tid
        else:
            if verbose:
                print "Ticket:\t%d" % tid
                print "Summary:"
                print "\t%s" % ticket['summary']
                print "Description:"
                for line in ticket['description'].splitlines():
                    print "\t%s" % line
                print "remaining time: %s%s" % (ticket['remaining_time'], 'h' if ticket['remaining_time'] != None else '') 
            else:
                print tid, ticket['summary']
    
    def get_components(self):
        '''get all components'''
        clist = self._safe_rpc(self.jsonrpc.ticket.component.getAll)
        return clist
    
    def show_components(self):
        '''print all defined components'''
        print "defined components:"
        for c in self.get_components():
            print c
    
    def get_milestones(self):
        '''get all milestones'''
        mslist = self._safe_rpc(self.jsonrpc.ticket.agilomilestone.getAll)
        return mslist
    
    def show_milestones(self, verbose=False):
        '''print all defined milestones'''
        print "defined Milestones:"
        for ms in self.get_milestones():
            print ms
    
    def get_priorities(self):
        '''get all priorities'''
        plist = self._safe_rpc(self.jsonrpc.ticket.priority.getAll)
        return plist
    
    def show_priorities(self, verbose=False):
        '''print all defined milestones'''
        print "defined priorities:"
        for p in self.get_priorities():
            print p
        
    def show_actions(self, tid, verbose=False):
        '''
        print a list of valid actions for a ticket
        '''
        actions = self._get_actions(tid)
        print "actions for ticket %d:" % tid
        for action in actions:
            print "\t%s" % action[0] if not verbose else action
        
        
    def _get_actions(self, tid):
        '''
        get valid actions for a ticket
        '''
        actions = self._safe_rpc(self.jsonrpc.ticket.getActions, tid)
        return actions
    
    def _action_is_valid(self, tid, action):
        '''
        checks if a given action is valid for a given ticket
        '''
        actions = self._get_actions(tid)
        actions = [action for line in actions for action in line[:1]]
        
        if action in actions:
            return True
        else:
            return False
    
    def _resolution_is_valid(self, tid, resolution=None):
        '''
        checks if resolution if resolution is contained in ticket actions as an option
        '''
        if resolution is None:
            return False
        actions = self._get_actions(tid)
        for actionline in actions:
            if actionline[0] == "resolve":
                if resolution in actionline[3][0][2]:
                    return True
        
        return False
        
    
    def edit_ticket(self, tid, comment=None):
        '''
        edits a ticket via texteditor, updates the ticket if contents changed
        '''
        
        editor = get_editor()
        if not editor:
            print "error: i do not know which editor to call, please set EDITOR environment variable"
            return

        ticket = self._get_ticket(tid)
        if not ticket:
            print "error: could not fetch ticket %d" % tid
            return

        tempfd, tempname = tempfile.mkstemp()
        utffd = codecs.open(tempname, "w", encoding="utf-8")
        ticket['description'] = ticket['description'].replace('\r\n', '\n')
        ticket['childlinks'] = ', '.join([str(x) for x in self.link_cache.get_ticket_childs(ticket['id'])])
        ticket['parentlinks'] = ', '.join([str(x) for x in self.link_cache.get_ticket_parents(ticket['id'])])
        utffd.write(self._smarterticket2text(ticket))
        utffd.close()

        editproc = subprocess.Popen(" ".join((editor, tempname)), shell=True)
        editproc.wait()
        
        #newticket = self._minimize_ticket(self._smartertext2ticket(codecs.open(tempname, "r", encoding="utf-8").read()))
        
        try:
            #newticket = self._minimize_ticket(self._smartertext2ticket(codecs.open(tempname, "r", encoding="utf-8").read()))
            newticket = self._smartertext2ticket(codecs.open(tempname, "r", encoding="utf-8").read())
        except Exception, e:
            print Exception, e
            os.remove(tempname)
            raise Exception
            #abort("exception")
            
        ticket['childlinks'] = [x for x in self.link_cache.get_ticket_childs(ticket['id'])]
        ticket['parentlinks'] = [x for x in self.link_cache.get_ticket_parents(ticket['id'])]
        """print "clinks:"
        pprint(newticket['childlinks'])
        pprint(ticket['childlinks'])
        print "plinks:"
        pprint(newticket['parentlinks'])
        pprint(ticket['parentlinks'])"""
        
        if newticket['childlinks'] != ticket['childlinks']:
            self.link_tickets(ticket['id'], newticket['childlinks'], deletenonlistedtargets=True)
            print "updated ticket child links"
        if newticket['parentlinks'] != ticket['parentlinks']:
            #print "updating parentlinks:"
            self.update_ticket_parentlinks(ticket['id'], newticket['parentlinks'])
            
        #can't just compare dicts here
        #ticket will have type & remaining_time set in most cases
        if ticket['summary'] != newticket['summary'] or ticket['description'] != newticket['description']\
            or ticket['priority'] != newticket['priority'] or ticket['milestone'] != newticket['milestone']:
            success, additional = self._update_ticket(tid, self._minimize_ticket(newticket), comment=comment)
            print "updated ticket via rpc"
            # fixme: check if successfull
        else:
            print "ticket didn't change - not updated(via rpc) - you saved bandwidth"
    
        
    def update_ticket_field(self, tid, fieldname, new_value, forbiddenvaluelist=[None,], comment=None):
        '''generic function to update a specific field in a ticket'''
        for fv in forbiddenvaluelist:
            if new_value == fv:
                print "error: '%s' not allowed for field %s." % (new_value, fieldname)
                return
        ticket = self._get_ticket(tid)
        if not ticket:
            print "could not fetch ticket %d" % tid
            return
        if not ticket.has_key(fieldname) or ticket[fieldname] != new_value:
            ticket[fieldname] = new_value
            self._update_ticket(tid, ticket, comment=comment)
        else:
            print "%s did not change - not updated - bandwidth saved" % (fieldname)
        return
    
        
    def update_remaining_time(self, tid, new_time, comment=None):
        '''
        udpates the remaining_time field of a ticket if it changed
        '''
        if new_time is None:
            print "error: I won't set remaining_time to 'None'"
            return
        
        ticket = self._get_ticket(tid)
        if not ticket:
            print "could not fetch ticket %d" % tid
            return
        
        old_time = None
        #new_time can be a int or float or str
        if isinstance(new_time, str):
            new_time = float(new_time) if '.' in new_time else int(new_time)
        
        #remaining_time is string
        if ticket['remaining_time'] != '' and ticket['remaining_time'] != None:
            old_time = ticket['remaining_time']
            old_time = float(old_time) if '.' in old_time else int(old_time)
            
        if old_time != new_time:
            ticket['remaining_time'] = new_time
            self._update_ticket(tid, ticket, comment=comment)
        else:
            print "remaining time did not change - not updated - bandwidth saved"
            
    
    def close_ticket(self, tid, resolution=None, comment=None):
        '''
        sets a ticket to closed or testing w/ corresponding resolution depending on ticket type
        '''
        ticket = self._get_ticket(tid)
        if not ticket:
            print "could not fetch ticket %d" % tid
            return
        
        #user can override story/bug closing (--> testing/sharing)
        #by setting a resolution
        if resolution is None and (ticket['type'] == 'story' or ticket['type'] == 'bug'):
            action = 'testing'
        elif resolution is not None:
            #only do the extra rpc call(check actions)
            #if user supplies custom resolution
            if not self._resolution_is_valid(tid, resolution):
                print "invalid resolution: %s" % resolution
                return
            ticket['action_resolve_resolve_resolution'] = resolution
            action = 'resolve'
        else:
            ticket['action_resolve_resolve_resolution'] = 'fixed'
            action = 'resolve'
        
        success, additional = self._update_ticket(tid, ticket, action, comment)
        #fixme: check if successfull
    
    
    def accept_ticket(self, tid, comment=None):
        '''
        accept a ticket, if it's valid actions include the accept action
        '''
        if not self._action_is_valid(tid, 'accept'):
            print "You cannot accept ticket %d" % tid
            return
        
        ticket = {}
        action = 'accept'
        success, additional = self._update_ticket(tid, ticket, action, comment)
        #fixme: check if successfull
        
    
    def reopen_ticket(self, tid, comment=None):
        '''
        reopen a ticket, if possible 
        '''
        
        if not self._action_is_valid(tid, 'reopen'):
            print "You cannot reopen ticket %d" % tid
            return
        
        ticket = {}
        action = 'reopen'
        success, additional = self._update_ticket(tid, ticket, action, comment)
        #fixme: check if successfull
        
    def _get_ticket_report(self, username=None, query=None):
        '''
        get a ticket report from trac
        '''
        query_base = "status=accepted&status=assigned&status=new\
&status=reopened&status=testing&group=type&order=priority\
&col=id&col=summary&col=status&col=type&col=priority\
&col=milestone&col=component"
        if query is None:
            if username is not None:
                query = "%s&owner=%s" % (query_base, username)
            else:
                query = query_base
        
        ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, query)
        tickets = []
        mc = self.multicall()
        for tid in ticket_ids:
            mc.ticket.get(tid)
        results = self._safe_rpc(mc)
        
        if results:
            for result in results.results['result']:
                tickets.append(self._get_ticket_from_rawticket(result['result']))
        
        return tickets
    
    def delete_tickets_by_query(self, query=None, verbose=None, doublecheck=False):
        if query is None:
            return None
        
        ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, query)
        ticket_types = []
        tickets = []
        mc = self.multicall()
        for tid in ticket_ids:
            mc.ticket.get(tid)
        results = self._safe_rpc(mc)
        for result in results.results['result']:
            tickets.append(self._get_ticket_from_rawticket(result['result']))
        
        allowed_types_2_delete = ['praise', 'problem', 'idea', 'question']
        #allowed_types_2_delete = ['praise', 'problem', 'question']
        for ticket in tickets:
            if ticket['type'] not in allowed_types_2_delete:
                #return False, "bad ticket type in query wont delete anything"
                raise Exception('delete_by_query_error', 'bad ticket type in query wont delete anything')
        
        if not doublecheck:
            print "would delete %d tickets" % len(tickets)
            return True,query
        else:
            mc = self.multicall()
            for tid in ticket_ids:
                mc.ticket.delete(tid)
                pass
            results = self._safe_rpc(mc)
            print "u just did a scary thing" 
        
        
    
    def show_ticket_report(self, username=None, verbose=False, termwidth=80, query=None):
        '''
        show a trac ticket report to the user
        '''
        if query is None:
            print "ticket report for '%s'" % username
        
        tickets = self._get_ticket_report(username=username, query=query)
        if verbose:
            for ticket in tickets:
                print "Ticket:\t%d" % ticket['id']
                print "Summary:"
                print "\t%s" % ticket['summary']
                print "Description:"
                for line in ticket['description'].splitlines():
                    print "\t%s" % line
                print "remaining time: %sh" % ticket['remaining_time'] if ticket['remaining_time'] is not None else '-'
                print ""
            
        else:
            print " ID  SUMMARY%sRT" % (' ' * (termwidth - 16))
            for ticket in tickets:
                truncated_line = ticket['summary'][0:termwidth-10]
                print "%4s %s %s%sh" % (ticket['id'],
                                        ticket['summary'][0:termwidth-10],
                                        ' '*(termwidth-10-len(truncated_line)),
                                        ticket['remaining_time'] if ticket['remaining_time'] is not None else '-')
    
    def simple_query(self, query=None, verbose=False, only_numbers=False, skip=None, maxlinewidth=80, tidlist=None, fieldlist=None, parentids=None, childids=None):
        '''query trac for tickets and print them in a readable way '''
        
        
        if (not query and not tidlist and not isinstance(parentids,list) and not isinstance(childids,list)):
            print "please supply a query or ticketids or parentids or childids"
            return
        elif tidlist and len(tidlist) < 1:
            print "id list has len 0. returning"
            return
        
        if query:
            ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, query) # XXX trac has max=100 many queries
        elif tidlist:
            ticket_ids = tidlist
        elif isinstance(parentids,list) or isinstance(childids,list):
            #get ALL TICKET
            ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, 'max=0')
        else:
            print "hmm should you ever reach this point? no query, no ticket ids, no parentids, no childids..."
            ticket_ids = []
        
        if skip:
            if skip > len(ticket_ids):
                print "with skip=%d, i would skip all tickets... skipping 0 tickets."
                skip = 0
            else:
                ticket_ids = ticket_ids[skip:]
        
        if isinstance(parentids,list):
            tmp_ticket_ids = []
            if len(parentids) > 0:
                for id in ticket_ids:
                    for pid in parentids:
                        if pid in self.link_cache.get_ticket_parents(id):
                            if id not in tmp_ticket_ids:
                                tmp_ticket_ids.append(id)
            else:
                #empty parentids list means get tickets that dont have any parents
                for id in ticket_ids:
                    if len(self.link_cache.get_ticket_parents(id)) == 0:
                        tmp_ticket_ids.append(id)
            
            ticket_ids = tmp_ticket_ids
        
        if isinstance(childids,list):
            tmp_ticket_ids = []
            if len(childids) > 0:
                for id in ticket_ids:
                    for pid in childids:
                        if pid in self.link_cache.get_ticket_childs(id):
                            if id not in tmp_ticket_ids:
                                tmp_ticket_ids.append(id)
            else:
                #empty childids list means get tickets that dont have any parents
                for id in ticket_ids:
                    if len(self.link_cache.get_ticket_childs(id)) == 0:
                        tmp_ticket_ids.append(id)
                
            ticket_ids = tmp_ticket_ids
        
        if only_numbers:
            idlist = ",".join(unicode(id) for id in ticket_ids)
            print "ticket IDs:"
            print idlist
            print ""
            print "fetched %s tickets" % len(ticket_ids)
            if skip > 0:
                print "%d tickets skipped" % skip
            return
        
        if not ticket_ids or len(ticket_ids) < 1:
            print "no tickets."
            return None
        
        tickets = []
        mc = self.multicall()
        for tid in ticket_ids:
            mc.ticket.get(tid)
        results = self._safe_rpc(mc)
        
        if results:
            for result in results.results['result']:
                tickets.append(self._get_ticket_from_rawticket(result['result']))
        
        if not fieldlist:
            summarywidth = maxlinewidth-(5+17+11)-1 # id,milestone,prio plus spaces minus one for summary spacing
            if summarywidth < 0:
                summarywidth = 1
            print u"{0:4} {1:{2}} {3:16} {4:10}".format('ID','summary',summarywidth,'milestone','priority')
            for t in tickets:
                print u"{0:4} {1:{2}.{3}} {4:16} {5:10}".format(t['id'],t['summary'],summarywidth,summarywidth, t['milestone'],t['priority'])
        else:
            #optional fieldlist that can be supplied via -f
            hparts = []
            for field in fieldlist:
                lpart = u"{0:{1}.{2}}".format(field[0],field[1],field[1])
                hparts.append(lpart)
            print u" ".join(hparts)
            for t in tickets:
                hparts = []
                for field in fieldlist:
                    if t.has_key(field[0]):
                        if isinstance(t[field[0]], (int,long)):
                            lpart = u"{0:{1}}".format(t[field[0]],field[1])
                        else:
                            lpart = u"{0:{1}.{2}}".format(t[field[0]],field[1],field[1])
                    else:
                        lpart =  u"{0:{1}.{2}}".format(' ',field[1],field[1])
                    hparts.append(lpart)
                    
                print u" ".join(hparts)
                
        print ""
        print "fetched %s tickets" % len(tickets)
        if skip > 0:
            print "%d tickets skipped" % skip
    
    def batch_edit(self, query=None, verbose=False, skip=None):
        ''' '''
        if not query:
            print "please supply a query"
            return
        ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, query)
        if skip:
            if skip > len(ticket_ids):
                print "with skip=%d, i would skip all tickets... skipping 0 tickets."
                skip = 0
            else:
                ticket_ids = ticket_ids[skip:]
        
        for id in ticket_ids:
            print "editing ticket %s" % id
            self.edit_ticket(id, comment=None)
            print "press any key to continue or CTRL-C to quit"
            tmpuser = raw_input()
            
    def interactive_batch_edit(self, query=None, skip=None, verbose=False):
        ''' a simple trac shell (hopefully)'''
        from tracshell import TracShell
        
        if not query:
            print "please supply a query"
            return
        ticket_ids = self._safe_rpc(self.jsonrpc.ticket.query, query)
        print "%d tickets returned by query" % len(ticket_ids)
        print "lala"
        
        
        
        for id in ticket_ids:
            #print "editing ticket %s" % id
            #self.edit_ticket(id, comment=None)
            #print "press any key to continue or CTRL-C to quit"
            shell = TracShell(tracrpc=self, ticketid=id)
            shell.run()
    
    def get_ticket_childlinks(self, tid):
        '''returns a list of ticketIDs that are targets of tid'''
        return self.link_cache.get_ticket_childs(tid)
    
    def get_ticket_parentlinks(self, tid):
        '''returns a list of ticketIDs that are sources of links to tid'''
        return self.link_cache.get_ticket_parents(tid)
        
    def get_ticket_links(self, tid):
        '''returns a dict of links of ticket tid. {'children': [], 'parents': []}'''
        return {'children': self.get_ticket_childlinks(tid), 'parents': self.get_ticket_parentlinks(tid)}
    
    def update_ticket_childlinks(self, tid=None, destids=None):
        '''wrapper'''
        if not tid:
            return
        return self.tracrpc.link_tickets(tid, destids, deletenonlistedtargets=True)
    
    def update_ticket_parentlinks(self, tid=None, newparentlistarg=[]):
        """updates parent links of a ticket
            get all parent tickets that are not linked to this child anymore
                delete this child from there
            
            get all parent tickets that are newly linked to this child
                link this child to that ticket  (pid, cid)
            
        """
        if not tid:
            return
        
        parentlinks = self.link_cache.get_ticket_parents(tid)
        deletedparents = []
        for pid in parentlinks:
            if pid not in newparentlistarg:
                deletedparents.append(pid)
        
        newparents = []
        for pid in newparentlistarg:
            if pid not in parentlinks:
                newparents.append(pid)
        
        for pid in deletedparents:
            self.delete_ticket_links(pid, [tid], updatecache=False)
        
        for pid in newparents:
            self.link_tickets(pid, [tid], deletenonlistedtargets=False, updatecache=False)
        self.link_cache.updatecache() #faster than calling it once after every link creation
            
        
    
    def delete_ticket_links(self, srcid=None, destids=None, updatecache=True):
        ''' '''
        if not srcid:
            print "no source ticket id specified for link deletion - returning"
            return
        
        if len(destids) < 1:
            print "no target ticket id(s) specified for link deletion - returning"
            return
        
        for tid in destids:
            self.httpbot.delete_ticket_link(srcid, tid)
        
        if updatecache:
            self.link_cache.updatecache()
             
    def link_tickets(self, srcid=None, destids=None, deletenonlistedtargets=False, updatecache=True):
        ''' '''
        
        if not srcid:
            print "no source ticket id specified for linking - returning"
            return
        
        if len(destids) < 1 and deletenonlistedtargets == True:
            srclinks = self.link_cache.get_ticket_childs(srcid)
            for tid in srclinks:
                self.httpbot.delete_ticket_link(srcid, tid)
            if updatecache:
                self.link_cache.updatecache()
            return
        
        if len(destids) < 1:
            print "no target ticket id(s) specified for linking - returning"
            return
        
        print "linking ticket %d with %s" % (srcid, destids)
        
        targetids = []
        #check that no duplicate link is tried to be created
        srclinks = self.link_cache.get_ticket_childs(srcid)
        if srclinks != None:
            for tid in destids:
                if tid not in srclinks:
                    targetids.append(tid)
                else:
                    print "ticket %d already linked with ticket %d. ignoring it." % (tid, srcid)
                    pass
        else:
            targetids = destids
        
        #delete ticket links not supplied as arg
        if deletenonlistedtargets and srclinks != None:
            for tid in srclinks:
                if tid not in destids:
                    self.httpbot.delete_ticket_link(srcid, tid)
        
        #check if targetIDs exist as tickets:
        #FIXME: here a multicall would be better
        for tid in targetids:
            if self._get_ticket(tid) == None:
                print "ticket %d does not exist.ignoring it" % tid 
                targetids.remove(tid)
        
        #check if src exists:
        if self._get_ticket(srcid) == None:
            print "src ticket %d does not exist. returning!" % srcid
            return
        
        #do the actual linking:
        for tid in targetids:
            self.httpbot.create_ticket_link(srcid, tid)
        if len(targetids) > 0 and updatecache:
            self.link_cache.updatecache()
        
    def linktest(self):
        #pprint(self._safe_rpc(self.jsonrpc.ticket.get, 2921))

        #self.link_tickets(2921, [1898, 2922])
        #self.link_tickets(2921, [1898], deletenonlistedtargets=True)
        self.link_tickets(2921, [2920], deletenonlistedtargets=False)
        #self.httpbot.delete_ticket_link(2921, 1898)
        #print "trying to link 504 w 2921 & 1337:"
        #self.link_tickets(504, [2921, 1337])
        



