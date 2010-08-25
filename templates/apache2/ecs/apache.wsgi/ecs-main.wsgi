#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import site

# writing to stdout as wsgi is considered an error
sys.stdout = sys.stderr

# Remember original sys.path.
prev_sys_path = list(sys.path)

#  source and environment location. 
appdir = '%(home)s/src/%(appname)s'
appbasedir = os.path.join(appdir, '..')
basedir = os.path.join(appdir, '..', '..')

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
sys.path.append(appdir)
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
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

