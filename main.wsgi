#!/usr/bin/env python
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
envdir = os.path.join(basedir, "environment/lib/python2.6/site-packages")
#print "ad %s, an %s, ab %s, b %s, e %s" % (appdir,appname,appbasedir,basedir,envdir) 

# Add each new site-packages directory.. 
site.addsitedir(envdir)

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

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
