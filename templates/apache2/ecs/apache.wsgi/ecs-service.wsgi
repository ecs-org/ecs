#!/usr/bin/env python
"""
Service WSGI Script
===================

"""

import cStringIO
import os

def application(environ, start_response):
    headers = []
    headers.append(('Content-Type', 'text/html'))
    write = start_response('200 OK', headers)
    input = environ['wsgi.input']
    output = cStringIO.StringIO()
    print >> output ("<html><head>Server Maintenance</head><body>Server Maintenance, please standby</body></html>")
    print >> output
    output.write(input.read(int(environ.get('CONTENT_LENGTH', '0'))))
    return [output.getvalue()]
