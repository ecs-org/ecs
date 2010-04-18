#!/usr/bin/env python
"""
Main WSGI Script
================

Currently does a lot of magic, but works.

WSGI Debug Helper
-----------------
if you have serious problems, comment out the rest of the script and run the code below instead, for debugging

import cStringIO
import os
def application(environ, start_response):
    headers = []
    headers.append(('Content-Type', 'text/plain'))
    write = start_response('200 OK', headers)
    input = environ['wsgi.input']
    output = cStringIO.StringIO()
    print >> output, "PID: %s" % os.getpid()
    print >> output, "UID: %s" % os.getuid()
    print >> output, "GID: %s" % os.getgid()
    print >> output
    keys = environ.keys()
    keys.sort()
    for key in keys:
        print >> output, '%s: %s' % (key, repr(environ[key]))
    print >> output
    output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))
    return [output.getvalue()]
"""

import os,sys,site

# Remember original sys.path.
prev_sys_path = list(sys.path)

#  source and environment location. 
x=__file__
if os.path.islink(x):
    x=os.readlink(x)

appdir = os.path.dirname(os.path.abspath(x))
appname = os.path.basename(appdir) 
appbasedir = os.path.join(appdir, "..")
basedir = os.path.join(appdir, "../..")

# FIXME: is hardcoded path names, and should be replaced
envdir = os.path.join(basedir, "environment")
sitedir = os.path.join(envdir, "/lib/python2.6/site-packages")
bindir = os.path.join(envdir, "bin")

#print "ad %s, an %s, ab %s, b %s, e %s" % (appdir,appname,appbasedir,basedir,envdir) 

# Add each new site-packages directory.. 
site.addsitedir(sitedir)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

# include django app basedir and set django settings
sys.path.append(appbasedir)
sys.path.append(appdir)
os.environ['DJANGO_SETTINGS_MODULE'] = appname+".settings"

# include environment bin dir at beginning of PATH
pathlist = os.environ['PATH'].split(os.pathsep)
try:
    pathlist.remove(bindir)
except ValueError:
    pass
pathlist.insert(0,bindir)
os.environ['PATH']= os.pathsep.join(pathlist)

# start wsgi main
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
