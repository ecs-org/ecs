# -*- coding: utf-8 -*-
'''
Created on Sep 22, 2010

@author: scripty
'''

import sys
if __name__ == "__main__":
    sys.path.insert(0,'../../../../')
    #print "path: %s" % sys.path
    
import os, urlparse, urllib
import ConfigParser
from pprint import pprint


_safe = ('abcdefghijklmnopqrstuvwxyz'
         'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
         '0123456789' '_.-/')
_safeset = None
_hex = None
def quotepath(path):
    '''quote the path part of a URL

    This is similar to urllib.quote, but it also tries to avoid
    quoting things twice (inspired by wget):

    >>> quotepath('abc def')
    'abc%20def'
    >>> quotepath('abc%20def')
    'abc%20def'
    >>> quotepath('abc%20 def')
    'abc%20%20def'
    >>> quotepath('abc def%20')
    'abc%20def%20'
    >>> quotepath('abc def%2')
    'abc%20def%252'
    >>> quotepath('abc def%')
    'abc%20def%25'
    '''
    global _safeset, _hex
    if _safeset is None:
        _safeset = set(_safe)
        _hex = set('abcdefABCDEF0123456789')
    l = list(path)
    for i in xrange(len(l)):
        c = l[i]
        if (c == '%' and i + 2 < len(l) and
            l[i + 1] in _hex and l[i + 2] in _hex):
            pass
        elif c not in _safeset:
            l[i] = '%%%02X' % ord(c)
    return ''.join(l)

def netlocsplit(netloc):
    '''split [user[:passwd]@]host[:port] into 4-tuple.'''

    a = netloc.find('@')
    if a == -1:
        user, passwd = None, None
    else:
        userpass, netloc = netloc[:a], netloc[a + 1:]
        c = userpass.find(':')
        if c == -1:
            user, passwd = urllib.unquote(userpass), None
        else:
            user = urllib.unquote(userpass[:c])
            passwd = urllib.unquote(userpass[c + 1:])
    c = netloc.find(':')
    if c == -1:
        host, port = netloc, None
    else:
        host, port = netloc[:c], netloc[c + 1:]
    return host, port, user, passwd

def getauthinfo(path):
    scheme, netloc, urlpath, query, frag = urlparse.urlsplit(path)
    
    if not urlpath:
        urlpath = '/'
    if scheme != 'file':
        # XXX: why are we quoting the path again with some smart
        # heuristic here? Anyway, it cannot be done with file://
        # urls since path encoding is os/fs dependent (see
        # urllib.pathname2url() for details).
        urlpath = quotepath(urlpath)
        
    host, port, user, passwd = netlocsplit(netloc)
    if user is not None:
        return {'user':user, 'password':passwd}
    else:
        return None


class ADAauth(object):
    '''
    classdocs
    '''
    credentials = []
    username = ''
    password = ''
    hgrc_files = []
    search_paths = []
    
    parsed_files = False
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def find_file(self, filename, startpath):
        needle = os.path.join(startpath, filename)
        if os.path.exists(needle):
            return needle
        else:
            return None
    
    def find_HGRC_files(self, paths):
        for startpath in paths:
            found_file = self.find_file('hgrc', startpath)
            if found_file != None:
                self.hgrc_files.append(found_file)
            found_file = self.find_file('.hgrc', startpath)
            if found_file != None:
                self.hgrc_files.append(found_file)
        
    def parse_files(self):
        for hgrc in self.hgrc_files:
            print "parsing %s" % hgrc
            tmpuser = tmppwd = None
            config = ConfigParser.SafeConfigParser()
            config.read(hgrc)
            
            try:
                url = config.get('paths', 'default')
                authinfo = getauthinfo(url)
                if authinfo is not None:
                    tmpuser = authinfo['user']
                    if authinfo['password'] is not None:
                        tmppwd = authinfo['password']
                    self.credentials.append({'username':tmpuser, 'password':tmppwd})
                    tmpuser = tmppwd = None
            except ConfigParser.NoSectionError:
                pass
            
            try:
                for item in config.items('auth'):
                    if "username" in item[0]:
                        tmpuser = config.get('auth', item[0])
                    if "password" in item[0]:
                        tmppwd = config.get('auth', item[0])
            except ConfigParser.NoSectionError:
                pass
            
            
            if tmpuser != None:
                self.credentials.append({'username':tmpuser, 'password':tmppwd})
        
    
    def try_2_find_auth_info(self):
        self.find_HGRC_files(self.search_paths)
        self.parse_files()
        self.parsed_files = True
    
    def prompt_for_pwd(self):
        import getpass
        return getpass.getpass("password: ")
    
    def prompt_for_user(self):
        sys.stdout.write("username: ")
        tmpuser = raw_input()
        print ""
        return tmpuser
    
    def get_credentials(self):
        if not self.parsed_files:
            self.try_2_find_auth_info()
            
        
        got_user_pwd = False
        for cred in self.credentials:
            #first one wins
            if cred['username'] != None and cred['password'] != None:
                got_user_pwd = True
                self.username = cred['username']
                self.password = cred['password']
                
            elif cred['username'] != None and cred['password'] == None and got_user_pwd == False:
                self.username = cred['username']
                self.password = self.prompt_for_pwd()
                cred['password'] = self.password
                got_user_pwd = True
                
        if not got_user_pwd:
            self.username = self.prompt_for_user()
            self.password = self.prompt_for_pwd()
        
        return [self.username, self.password]
