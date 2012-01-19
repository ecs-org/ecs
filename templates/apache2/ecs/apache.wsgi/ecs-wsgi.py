#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import site
import StringIO

# writing to stdout as wsgi is considered an error, and borks wsgi setup
sys.stdout = sys.stderr

# Remember original sys.path.
prev_sys_path = list(sys.path)

#  source and environment location. 
srcbasedir = '%(source)s'
appdir = os.path.join(srcbasedir, '%(appname)s')
basedir = os.path.join(srcbasedir, '..')

# TODO: partly hardcoded path names, and should be replaced
envdir = os.path.join(basedir, "environment")
sitedir = os.path.join(envdir, "/lib/python2.6/site-packages")
bindir = os.path.join(envdir, "bin")
service_indicator  = os.path.join(basedir, 'ecs-conf', 'service.now')

# Add each new site-packages directory.. 
site.addsitedir(sitedir)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

# include src basedir in python path and set django settings
sys.path.append(srcbasedir)
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

# maintenance loop (so we can be sure no django is accessing database or therelike)
def maintenance(environ, start_response):
    headers = []
    headers.append(('Content-Type', 'text/html'))
    write = start_response('200 OK', headers)
    input = environ['wsgi.input']
    
    with StringIO.StringIO() as output:
        print >> output, "<html><head>Server Maintenance</head><body>Server Maintenance, please standby</body></html>"
        print >> output
        output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))
        data = output.getvalue()
        
    return [data]

# late import of django, because we needed to mangle python paths first, to include environment
import django.core.handlers.wsgi

# start wsgi main or maintenance, depending existence of service_indicator
if os.path.exists(service_indicator):
    application = maintenance
else:
    application = django.core.handlers.wsgi.WSGIHandler()

