# -*- coding: utf-8 -*-
"""
simple interactive shell for editing multiple tickets
trying to wrapup tracrpc functionality in an interactive shell 
"""

'''
Created on Mar 3, 2011

@author: scripty
'''

import cmd
import readline
import sys
import os
import optparse
import textwrap

from pprint import pprint

def get_homedir():
    if sys.platform in ['win32', 'cygwin']:
        from win32com.shell import shell,shellcon
        home = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)
        return home
        #return os.environ['USERPROFILE']
    else:
        return os.environ['HOME']



class ShellOptParser(optparse.OptionParser):
    '''OptParser derived class for special errorhandling'''
    
    def __init__(self):
        optparse.OptionParser.__init__(self)
        #cmd.Cmd.__init__(self)
    
    def error(self, msg):
        '''my own option parser error handling function that does not exit, it throws an optionparseException'''
        print msg
        #self.print_usage(sys.stderr)
        raise Exception('option parsing error')
        #return
    
        
"""'q': 'query $0',
    'v': 'view $0',
    'e': 'edit $0',
    'c': 'create $0',
    'log': 'changelog $0',
    'Q': 'quit',
    'EOF': 'quit',"""
DEFAULT_ALIASES = {
    'v': 'view $0',
    'g': 'get $0',
    'q': 'query $0',
    'qe': 'queryedit $0',
    'pqe': 'pausequeryedit',
    'sqe': 'stopqueryedit',
    'Q': 'quit',
    'b': 'previousticket',
    '<': 'previousticket',
    'n': 'nextticket',
    '>': 'nextticket',
    'e': 'edit $0',
    'm': 'milestone',
    'c': 'component',
    'pl': 'parentlinks',
    'cl': 'childlinks',
    'l': 'links',
    'p': 'setpriority',
    's': 'status',
    'sm': 'showmilestones',
    'milestones': 'showmilestones',
    'pt': 'parsetest $0',
    'rt': 'remainingtime $0',
    'eta': 'remainingtime $0',
    'r':  'removefromquery',
    'a':  'addtoquery $0',
    
    
}

class TracShell(cmd.Cmd):
    '''
    classdocs
    '''
    tracrpc = None
    ticketid = None
    singleticketmode = False
    
    username = None
    
    batcheditmode = False
    batchquery = None
    batchticketlist = None
    batchskip = None
    batchticketindex = None
    currentticketid = None
    currentticket = None
    currentticketchangelog = None
    
    maxlinewidth = 80
    printsummaryonfetch = True
    append_max0_toquery = True
    changelogfieldstoignore = ['comment']
    
    #future use:
    batchprefetch = 0
    changelogfields2honor = ['milestone','priority',]
    
    stdprompt = 'tshell> '
    optparser = None
    
    def __init__(self, tracrpc=None, ticketid=None, tracpath=None, debug=False):
        '''
        Constructor
        '''
        
        histfile = os.path.join(get_homedir(), ".tracshellhist")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        
        import atexit
        atexit.register(readline.write_history_file, histfile)
        del histfile

        #self.optparser = ShellOptParser()
        #tracrpc lolfoo...
        if not tracrpc:
            #print "pass a tacrpc instance as arg. scripty's OOriented foo lol is very lol..."
            #return None
            from deployment.utils import fabdir
            sys.path.append(fabdir())
            from deployment.ada.issuetracker import _getbot
            self.tracrpc, self.username = _getbot(tracpath=tracpath, debug=debug)
        else:    
            self.tracrpc = tracrpc
        
        if ticketid:
            try:
                self.ticketid = int(ticketid)
                self.singleticketmode = True
            except ValueError:
                print "non integer value supplied to tracshell as ticketid"
                return None
        
        cmd.Cmd.__init__(self)
        self.prompt = self.stdprompt
        self.aliases = {}
        self.aliases.update(DEFAULT_ALIASES)
    
    def refetchticketafteredit(fn):
        '''my funky decorator to refetch the current ticket, after the function returned'''
        def wrapped(self, *args, **kwargs):
            #print "calling func:%s" % fn
            ret = fn(self, *args, **kwargs)
            #print "refetching ticket"
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
            return ret
        
        return wrapped
    
    def do_status(self, args):
        '''display internal status/mode information'''
        print "batcheditmode:",self.batcheditmode
        print "currentticketid:",self.currentticketid
        print "currentticketidindex:",self.batchticketindex
        print "batchquery:",self.batchquery
        print "batchskip:",self.batchskip
        print "batchticketlist:",self.batchticketlist
        print "maxlinewidth:",self.maxlinewidth
        print "printsummaryonfetch:",self.printsummaryonfetch
        print "append_max0_toquery:",self.append_max0_toquery
        print "changelogfieldstoignore",self.changelogfieldstoignore
        
    
    def do_help(self, args):
        '''help'''
        cmd.Cmd.do_help(self,args)
        """
        if self.batcheditmode:
            print "e to edit (summary,description)"
            print "m for milestone"
            print "c for component"
            print "l for ticket links"
            print "p for priority"
            print "b or < for previous ticket"
            print "n or > for next ticket"
        """
    
    def do_bugs(self, args):
        '''list known issues'''
        print "known issues/bugs:"
        print "max=0 is not added automagically to queries - u have to always use -m"
        print "(hard) abort on queries that dont return any tickets"
        print "testtrac #1898 cant edit component"
        print "prompt displays ticket id even if that ticket does not exist (testtrac: g 11)"
        print "ticket linking does not work as expected"
        print "    is first: permission problem, and second: some other fancy stuff, it seems to be an error only if tshell is used on ecsdev server."
        print "documentation / intro for the whole thing"
        print ""
    
    def do_maxlinewidth(self,args):
        '''set the maximum width for output'''
        parser = ShellOptParser()
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply length as argument"
            return
        try:
            int(args[0])
        except ValueError:
            print "please supply an integer"
            return
        self.maxlinewidth = int(args[0])
         
    def do_aliases(self, args):
        '''list aliases'''
        print "defined aliases:"
        for alias,cmd in DEFAULT_ALIASES.iteritems():
            print '%s\t%s' % (alias, cmd)
    
    def parsercleanup(fn):
        ''' decorator to remove all options from optparser instance does not work...'''
        print "not implemented"
        return
        def wrapped(self, *args, **kwargs):
            print "decorator not implemented!!!"
            ret = fn(self, *args, **kwargs)
            """
            print "cleaning optparser:"
            
            print "options present:"
            for opt in self.optparser.option_list:
                print "option:",opt.get_opt_string()
                
            print ""
            print "cleaning"
            print ""
            for opt in self.optparser.option_list:
                self.optparser.remove_option(opt.get_opt_string())
            
            for opt in self.optparser.option_list:
                print "option:",opt.get_opt_string()
            
            print "cleaning done"
            """
            return ret
        
        return wrapped
    
    
    def run(self):
        #print "tracshell:"
        if self.singleticketmode:
            print "ticket:",self.ticketid
        else:
            pass
        
        self.cmdloop("ecsdev tracshell")
    
            
    def postcmd(self, stop, line):
        ''' '''
        if self.batcheditmode:
            self.prompt = "batch>ID-%d: " % self.currentticketid
        elif not self.batcheditmode and self.currentticketid != None:
            self.prompt = "single>ID-%d: " % self.currentticketid
        else:
            self.prompt = self.stdprompt
        
        cmd.Cmd.postcmd(self, stop, line)
        
    
    def do_test(self, args=None):
        '''a test method'''
        print "test method"
        print "args:",args
        
    def do_quit(self, _):
        """
        Quit the program
        Shortcut: Q
        """
        # cmd.Cmd passes an arg no matter what
        # which we don't care about here.
        # possible bug?
        print "Goodbye!"
        sys.exit()
        
    def emptyline(self):
        """Method called when an empty line is entered in response to the prompt. If this method is not overridden, it repeats the last nonempty command entered."""
        return
    
    def precmd(self, line):
        """handles alias commands for line (which can be a string or list of args)"""
        if isinstance(line, basestring):
            parts = line.split(' ')
        else:
            parts = list(line)
            line = ' '.join(line)
        cmd = parts[0]
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
            #print "cmd:",cmd
            args = parts[1:]
            unused_args = [] # they go into $0 if it exists
            for index, arg in enumerate(args):
                #print "i:",index,"arg:",arg
                param_placeholder = '$%d' % (index + 1)
                if param_placeholder in cmd:
                    cmd = cmd.replace(param_placeholder, arg)
                else:
                    unused_args.append(arg)
            if unused_args and '$0' in cmd:
                cmd = cmd.replace('$0', ' '.join(unused_args))
                #print "cmd:",cmd
            #print "returning cmd:"
            #pprint(cmd)
            return cmd
        else:
            #print "returning line:"
            #pprint(line)
            return line
    
    
    #@parsercleanup
    @refetchticketafteredit
    def do_edit(self, args):
        '''edit a ticket. [-c <commenttext>]'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        parser.add_option('-c', '--comment', action='store', dest='comment', default=None)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.currentticketid:
            print("at least one ticket id is needed.")
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        elif len(args) == 0 and self.currentticketid:
            tid = self.currentticketid
        else:
            try:
                tid = args[0]
            except ValueError:
                print "only ints are valid ticket IDs"
                return
        
        self.tracrpc.edit_ticket(tid, comment=opts.comment)
    
    def do_forget(self, args):
        '''forget the current ticket - only in non batchmode'''
        if self.batcheditmode:
            print "error: batcheditmode is on. this only works in non batchmode"
        else:
            self.currentticketid = None
            self.currentticket = None
            self.currentticketchangelog = None
        
    def do_get(self, args):
        '''get ticket specified by ID: >get <ID>
        fetches the ticket for interactive editing.'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.batcheditmode:
            print("at least one ticket id is needed.")
            return
        
        
        try:
            tid = int(args[0])
        except ValueError:
            print "only integers are valid ticket IDs"                
            return
        
        if self.batcheditmode and tid not in self.batchticketlist:
            print "that ticket is not in your current query. use 'pausequeryedit' or 'stopqueryedit'..."
            return
        elif self.batcheditmode and tid in self.batchticketlist:
            self.batchticketindex = self.batchticketlist.index(tid)
            self.currentticketid =  tid
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        else:
            self.currentticketid =  tid
            self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True) 
        
        if not self.currentticket:
            self.currentticketid = None
        
        if self.printsummaryonfetch and self.currentticket != None:
            print u"  {0:{1}.{2}}".format(self.currentticket['summary'], self.maxlinewidth-2, self.maxlinewidth-2)
    
    
    def do_changelog(self, args):
        '''show changelog of current ticket or ticket <ID> supplied as arg'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.currentticketid:
            print("no ticket id for me, no changelog for you.")
            return
        
        if len(args) > 0:
            try:
                tid = int(args[0])
            except ValueError:
                print "only ints are valid ticket IDs"
                return
        elif self.currentticketid != None:
            tid = self.currentticketid
        else:
            print "you should not end up here. no ticket id to work on..."
            return
        
        
        #if tid == self.currentticketid:
        #    self.print_ticketchangelog(self.currentticketchangelog)            
        #else:
        #    self.print_ticketchangelog(self.tracrpc._get_ticket_changelog(tid))
        self.print_ticketchangelog(self.tracrpc._get_ticket_changelog(tid))
            
    def do_view(self, args):
        '''view a ticket: view <ID> [-v|--verbos=]'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tid = None
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1 and not self.currentticketid:
            print("at least one ticket id is needed.")
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        elif len(args) == 0 and self.currentticketid:
            tid = self.currentticketid
        else:
            try:
                tid = int(args[0])
            except ValueError:
                print "only ints are valid ticket IDs"
                return
        
        if tid == self.currentticketid:
            self.print_ticket(self.currentticket)            
        else:
            self.print_ticket(self.tracrpc._get_ticket(tid, getlinks=True))
        
    
    
    def do_query(self, args):
        '''query trac for tickets. 
        query <tracquery> [-s <int> - skip int tickets] [-m - add max0 to query] [-n - only output ticket IDs]'''
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        parser.add_option('-s', '--skip', action='store', dest='skip', type='int', default=0)
        parser.add_option('-n', '--onlynumbers', action='store_true', dest='only_numbers', default=False)
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        parser.add_option('-f', '--fields', action='store', dest='tmpfields', default=None, help="ticket fields to display")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply a query"
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        
        q = args[0]
        if not "&max=0" in q and (self.append_max0_toquery or opts.addmax0 == True):
            q = '%s&max=0' % q
        
        #optional fieldlist that can be supplied via -f
        fields = None
        if opts.tmpfields:
            tmpfields = [f.strip() for f in opts.tmpfields.split(',')]
            fields = zip(tmpfields[0::2], tmpfields[1::2])
            
        self.tracrpc.simple_query(query=q, only_numbers=opts.only_numbers, skip=opts.skip, maxlinewidth=self.maxlinewidth, fieldlist=fields)
    
    
    def do_showqueryset(self, args):
        '''display a summary of all tickets in current queryset
        showqueryset [-n show - ticket IDs only]'''
        
        if not self.batcheditmode:
            print "this is for batchedit mode only"
            return
        
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        parser.add_option('-s', '--skip', action='store', dest='skip', type='int', default=0)
        parser.add_option('-n', '--onlynumbers', action='store_true', dest='only_numbers', default=False)
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        self.tracrpc.simple_query(query=None, only_numbers=opts.only_numbers, skip=opts.skip, maxlinewidth=self.maxlinewidth, tidlist=self.batchticketlist)
    
    
    def do_addtoquery(self, args):
        '''add ticket specified by <ID> to current queryset'''
        if not self.batcheditmode:
            print "this is for batchedit mode only"
            return
        
        parser = ShellOptParser()
        parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)
        tids = []
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply a ticket ID to add as argument"
            return
        
        for arg in args:
            try:
                tid = int(arg)
                if tid not in self.batchticketlist:
                    if self.tracrpc._get_ticket(tid) != None:
                        self.batchticketlist.append(tid)
                        print "added ticket %d" % tid
            except ValueError:
                print "malformed argument '%s' ignored" % arg
        
    
         
    
    def do_removefromquery(self, args):
        '''remove current ticket from current queryset'''
        
        if not self.batcheditmode:
            print "this is for batchedit mode only"
            return
        
        parser = ShellOptParser()
        tids = []
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        
        #ticket IDs supplied as args
        for arg in args:
            try:
                tid = int(arg)
                if tid in self.batchticketlist:
                    self.batchticketlist.remove(tid)
                    print "removed ticket %d" % tid
                    if len(self.batchticketlist) < 1:
                        print "no more tickets in query set. stopping queryedit mode."
                        self._stop_queryedit()
                        return
                else:
                    print "ticket %d not in current queryset. ignored" % tid
                        
            except ValueError:
                print "malformed argument '%s' ignored" % arg
        
        #current ticket (if no arg was supplied)
        if len(args) < 1:
            self.batchticketlist.remove(self.currentticketid)
            if len(self.batchticketlist) < 1:
                print "no more tickets in query set. stopping queryedit mode."
                self._stop_queryedit()
                return
        
        #try to stay sane:
        if self.batchticketindex > len(self.batchticketlist)-1:
            self.batchticketindex = len(self.batchticketlist)-1
        
        self.currentticketid = self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        
        if self.printsummaryonfetch and self.currentticket != None:
            print u"  {0:{1}.{2}}".format(self.currentticket['summary'], self.maxlinewidth-2, self.maxlinewidth-2)
    
    def do_queryedit(self, args):
        '''batch edit a series of tickets.
        query <tracquery> [-s <int> - skip int tickets] [-m - add max0 to query]'''
        parser = ShellOptParser()
        parser.add_option('-s', '--skip', action='store', dest='skip', type='int', default=0)
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        if len(args) < 1:
            print "please supply a query"
            return
        elif len(args) > 1:
            print "too many arguments"
            return
        
        q = args[0]
        if not "&max=0" in q and (self.append_max0_toquery or opts.addmax0 == True):
            q = '%s&max=0' % q
        
        skip = opts.skip
        self.batcheditmode = True
        self.batchquery = q
        self.batchticketlist = None
        self.batchskip = skip
        
        ticket_ids = self.tracrpc._safe_rpc(self.tracrpc.jsonrpc.ticket.query, q)

        if skip > len(ticket_ids):
            print "with skip=%d, i would skip all tickets... skipping 0 tickets."
            skip = 0
        
        self.batchticketlist = ticket_ids[skip:]
        
        print "%d tickets fetched - %s skipped" % (len(ticket_ids), skip)
        self.batchticketindex = 0
        self.currentticketid =  self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        
        if self.printsummaryonfetch and self.currentticket != None:
            print u"  {0:{1}.{2}}".format(self.currentticket['summary'], self.maxlinewidth-2, self.maxlinewidth-2)
        
        return
    
    def do_pausequeryedit(self, args):
        '''pause a query edit session'''
        print "not implemented!"
        return
    
    def do_stopqueryedit(self,args):
        '''stop a query edit session'''
        tmp = raw_input("sure? (y/n)")
        if tmp.lower() == 'y':
            self._stop_queryedit()
        else:
            print "continuing query edit session"
    
    def _stop_queryedit(self):
        self.batcheditmode = False
        self.batchquery = None
        self.batchskip = None
        self.batchticketindex = None
        self.batchticketlist = None
        self.currentticketid = None
        self.currentticket = None
        self.currentticketchangelog = None
    
    def do_previousticket(self, args):
        '''select the previous ticket in batchedit mode'''
        if not self.batcheditmode:
            print "not in batcheditmode!"
            return
        if self.batchticketindex-1 < 0:
            self.batchticketindex = len(self.batchticketlist)-1
            print "wrapped: giving you the last ticket"
        else:
            self.batchticketindex -= 1
        
        self.currentticketid = self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        
        if self.printsummaryonfetch and self.currentticket != None:
            print u"  {0:{1}.{2}}".format(self.currentticket['summary'], self.maxlinewidth-2, self.maxlinewidth-2)
    
    def do_nextticket(self, args):
        '''select the next ticket in batchedit mode'''
        if not self.batcheditmode:
            print "not in batcheditmode!"
            return
        
        if self.batchticketindex+1 > len(self.batchticketlist)-1:
            self.batchticketindex = 0
            print "wrapped: giving you the first ticket"
        else:
            self.batchticketindex += 1
        
        self.currentticketid = self.batchticketlist[self.batchticketindex]
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        
        if self.printsummaryonfetch and self.currentticket != None:
            print u"  {0:{1}.{2}}".format(self.currentticket['summary'], self.maxlinewidth-2, self.maxlinewidth-2)
    
    
    @refetchticketafteredit
    def do_component(self,args):
        '''set component of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_components())
        print "current component: '%s'" % self.currentticket['component']
        component = raw_input('new component: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='component', new_value=component, forbiddenvaluelist=[None,], comment=None)
    
    @refetchticketafteredit
    def do_milestone(self,args):
        '''set milestone of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_milestones())
        print "current milestone: '%s'" % self.currentticket['milestone']
        milestone = raw_input('new milestone: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='milestone', new_value=milestone, forbiddenvaluelist=[None,], comment=None)
    
    @refetchticketafteredit
    def do_parentlinks(self,args):
        '''set parentlinks of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current parents: ", self.currentticket['parents']
        idlist = []
        linkline = raw_input('new linklist(willoverwrite): ')
        sepchar = ' '
        if ',' in linkline:
            sepchar = ','
        tmpidlist = linkline.split(sepchar)
        idlist = []
        for id in tmpidlist:
            if id != '':
                try:
                    idlist.append(int(id))
                except ValueError:
                    print "only integers are valid ticket IDS!"
                    return
        
        print "new parents: ", ', '.join([str(id) for id in idlist])
        print "non listed links will be removed!"
        choice = raw_input("correct? (y/n) :")
        if choice.lower() == 'y':
            self.tracrpc.update_ticket_parentlinks(self.currentticketid, newparentlistarg=idlist)
        
    @refetchticketafteredit
    def do_childlinks(self,args):
        '''set childlinks of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current children: ", self.currentticket['children']
        linkline = raw_input('new linklist(willoverwrite): ')
        sepchar = ' '
        if ',' in linkline:
            sepchar = ','
        tmpidlist = linkline.split(sepchar)
        idlist = []
        for id in tmpidlist:
            if id != '':
                try:
                    idlist.append(int(id))
                except ValueError:
                    print "only integers are valid ticket IDS!"
                    return
        
        print "new children: ", ', '.join([str(id) for id in idlist])
        print "non listed links will be removed!"
        choice = raw_input("correct? (y/n) :")
        if choice.lower() == 'y':
            self.tracrpc.link_tickets(self.currentticketid, idlist, deletenonlistedtargets=True)
        
    
    def do_queryset_adopt(self, args):
        '''add arguments(IDs) as children of all tickets in current queryset
        think: the queryset adopts the arguments'''
        parser = ShellOptParser()
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        idlist = []
        for arg in args:
            try:
                idlist.append(int(arg))
            except ValueError:
                print "malformed argument '%s' ignored." % arg
        
        for srcid in self.batchticketlist:
            self.tracrpc.link_tickets(srcid, idlist, deletenonlistedtargets=False)
        
        #refetch
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
        
    def do_queryset_procreate(self, args):
        '''add arguments(IDs) as parents of all tickets in current queryset
        think: the arguments adopt the queryset'''
        parser = ShellOptParser()
        parser.add_option('-m', '--max0', action='store_true', dest='addmax0', default=False, help="add max=0 to query")
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        
        idlist = []
        for arg in args:
            try:
                idlist.append(int(arg))
            except ValueError:
                print "malformed argument '%s' ignored." % arg
        
        for parentid in idlist:
            for tid in self.batchticketlist:
                self.tracrpc.link_tickets(parentid, [tid], deletenonlistedtargets=False)
        
        #refetch
        self.currentticket = self.tracrpc._get_ticket(self.currentticketid, getlinks=True)
    
    @refetchticketafteredit
    def do_links(self,args):
        '''set links of a ticket'''
        print "not implemented yet - use childlinks or parentlinks command instead"
        return
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "current children: ", self.currentticket['children']
        print "current parents: ", self.currentticket['parents']
        
    @refetchticketafteredit   
    def do_setpriority(self,args):
        '''set priority of a ticket'''
        if not self.currentticketid:
            print "no ticket set - use 'get ID' or do a queryedit"
            return
        print "possible values:",', '.join(self.tracrpc.get_priorities())
        print "current priority: '%s'" % self.currentticket['priority']
        priority = raw_input('new priority: ')
        self.tracrpc.update_ticket_field(self.currentticketid, fieldname='priority', new_value=priority, forbiddenvaluelist=[None,], comment=None)
    
    
    def do_showmilestones(self,args):
        '''show all defined milestones'''
        self.tracrpc.show_milestones()
    
    def do_showpriorities(self, args):
        '''show all defined priorities'''
        self.tracrpc.show_priorities()
    
    def do_showcomponents(self, args):
        '''show all defnied components'''
        self.tracrpc.show_components()
    
    @refetchticketafteredit
    def do_remainingtime(self, args):
        '''udpate the remaining time of the current ticket.
        >remainingtime <float or int>'''
        if not self.currentticketid:
            print "please get a ticket first. g <ticketid>"
            return
        
        parser = ShellOptParser()
        try:
            (opts, args) = parser.parse_args(args.split())
            if '$0' in args:
                args.remove('$0')
        except Exception as e:
            print e
            return
        if len(args) < 1:
            print "argument needed"
            return
        if len(args) > 1:
            print "too many arguments"
            return
        
        new_time=None
        try:
            new_time=float(args[0])
        except ValueError,e:
            print "bad argument. i want ints or floats"
            return
        
        print "new time:", new_time," type:",type(new_time)
        self.tracrpc.update_remaining_time(self.currentticketid, new_time, comment=None)
    
    def print_ticket(self,ticket):
        '''print a ticket'''
        keymaxlen=0
        for k,v in ticket.iteritems():
            if len(k) > keymaxlen:
                keymaxlen=len(k)
        
        print ""
        
        k="ticket"
        print u"ticket:%s%s" % (' '*(keymaxlen-len(k)+1), ticket['id'])
        k="summary"
        print u"summary:%s%s" % (' '*(keymaxlen-len(k)+1),ticket['summary'])
        
        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = "  "
        wrapper.subsequent_indent = "  "
        wrapper.width = 60
        print u"description:"
        print wrapper.fill(text=ticket['description'])
        
        for k,v in ticket.iteritems():
            if k not in ['id', 'summary', 'description']:
                print u"%s:%s%s" % (k,' '*(keymaxlen-len(k)+1), v)
        
    def print_ticketchangelog(self, changelog):
        '''print a nice summary of the ticket changelog'''
        
        if not changelog or len(changelog) < 1:
            print "no changes"
            return
        
        wrapper = textwrap.TextWrapper()
        wrapper.initial_indent = "    "
        wrapper.subsequent_indent = "    "
        wrapper.width = 60
        
        for entry in changelog:
            cdate = entry[0]
            user = entry[1]
            field = entry[2]
            old = entry[3]
            new = entry[4]
            if field in self.changelogfieldstoignore:
                continue
            
            if field not in ['description', 'summary']:
                print u"{0}: {1}: '{2}' => '{3}'".format(cdate.strftime("%a %b %d %H:%M:%S %Y"), field, old, new)
            else:
                print u"{0}: {1} changed from:".format(cdate.strftime("%a %b %d %H:%M:%S %Y"), field)
                print wrapper.fill(text=old)
                print "  to:"
                print wrapper.fill(text=new)
            #print ""
                
        #pprint(changelog)
        
        
    
    
    
if __name__ == '__main__':
    s = TracShell()
    s.run()


