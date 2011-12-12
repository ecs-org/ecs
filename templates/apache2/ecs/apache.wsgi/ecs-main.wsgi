#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import site

# writing to stdout as wsgi is considered an error, and borks wsgi setup
sys.stdout = sys.stderr

# Remember original sys.path.
prev_sys_path = list(sys.path)

#  source and environment location. 
srcbasedir = '%(source)s'
appdir = os.path.join(srcbasedir, '%(appname)s')
basedir = os.path.join(srcbasedir, '..')

# FIXME: is hardcoded path names, and should be replaced
envdir = os.path.join(basedir, "environment")
sitedir = os.path.join(envdir, "/lib/python2.6/site-packages")
bindir = os.path.join(envdir, "bin")

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
os.environ['DJANGO_SETTINGS_MODULE'] = '%(appname)s.settings'

# include environment bin dir at beginning of PATH
pathlist = os.environ['PATH'].split(os.pathsep)
try:
    pathlist.remove(bindir)
except ValueError:
    pass
pathlist.insert(0,bindir)
os.environ['PATH']= os.pathsep.join(pathlist)

# tell celery to load its settings from djcelery (which uses django settings.py)
os.environ["CELERY_LOADER"] = "djcelery.loaders.DjangoLoader"


# start wsgi main

def maintenance(environ, start_response):
    headers = []
    headers.append(('Content-Type', 'text/html'))
    write = start_response('200 OK', headers)
    input = environ['wsgi.input']
    output = cStringIO.StringIO()
    print >> output, "<html><head>Server Maintenance</head><body>Server Maintenance, please standby</body></html>"
    print >> output
    output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))
    return [output.getvalue()]

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

