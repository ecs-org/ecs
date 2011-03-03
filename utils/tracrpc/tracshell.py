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
import sys

from pprint import pprint
from deployment.utils import get_homedir, fabdir, import_from
from deployment.utils import strbool as _strb, strbool

"""'q': 'query $0',
    'v': 'view $0',
    'e': 'edit $0',
    'c': 'create $0',
    'log': 'changelog $0',
    'Q': 'quit',
    'EOF': 'quit',"""
DEFAULT_ALIASES = {
    'v': 'view $0',
    'q': 'query $0',
    'qe': 'queryedit $0',
    'Q': 'quit',
    'b': 'previousticket',
    '<': 'previousticket',
    'n': 'nextticket',
    '>': 'nextticket',
    'e': 'edit $0',
    'm': 'milestone',
    'c': 'component',
    'l': 'parentlinks',
    
}

class TracShell(cmd.Cmd):
    '''
    classdocs
    '''
    tracrpc = None
    ticketid = None
    singleticketmode = False
    batcheditmode = False
    batchquery = None
    username = None
    
    def __init__(self, tracrpc=None, ticketid=None, tracpath=None, debug=False):
        '''
        Constructor
        '''
        
        #tracrpc lolfoo...
        if not tracrpc:
            #print "pass a tacrpc instance as arg. scripty's OOriented foo lol is very lol..."
            #return None
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
        self.aliases = {}
        self.aliases.update(DEFAULT_ALIASES)
        
    def run(self):
        print "tracshell:"
        if self.singleticketmode:
            print "ticket:",self.ticketid
        else:
            pass
        
        self.cmdloop("introbanner")
    
    def do_test(self, args=None):
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
    
    def do_edit(self, args):
        '''edit a ticket'''
        tid = None
        comment = None
        arglist = args.split(',')
        argc = len(arglist)
        if argc > 0:
            try:
                tid = int(arglist[0].strip())
            except ValueError:
                print "non integer value passed as argument"
                return None
        if argc > 1:
            comment = arglist[1].strip()
        self.tracrpc.edit_ticket(tid, comment=comment)
        return
    
    def do_view(self, args):
        '''view a ticket: view (int)ID[,True(verbose output)]'''  
        tid = None
        verbose = False
        arglist = args.split(',')
        argc = len(arglist)
        if argc > 0:
            try:
                tid = int(arglist[0].strip())
            except ValueError:
                print "non integer value passed as argument"
                return None
        else:
            print "please supply a ticket id"
            return
        if argc > 1:
            verbose = strbool(arglist[1].strip())
                
        self.tracrpc.show_ticket(tid, verbose=verbose)
        return
    
    def do_queryedit(self, args):
        '''batch edit a series of tickets,params: query,[(int)skip]'''
        return
    
    def do_query(self, args):
        '''query trac for tickets,params: query,[(int)skip],[True|False (output only numbers]'''
        q = None
        skip = None
        only_numbers=False
        arglist = args.split(',')
        argc = len(arglist)
        if argc > 0:
            q = arglist[0]
        else:
            print "please supply a query"
            return
        if argc > 1:
            try:
                skip = int(arglist[1].strip())
            except ValueError:
                 print "please pass an int as skip param, ignoring skip for now"
                 skip = None
        if argc > 2:
            only_numbers = strbool(arglist[2])
        
        self.tracrpc.simple_query(query=q, only_numbers=only_numbers, skip=skip)
        
if __name__ == '__main__':
    s = TracShell()
    s.run()


