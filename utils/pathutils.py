# -*- coding: utf-8 -*-

import os
import tempfile

from django.conf import settings


def which(file, mode=os.F_OK | os.X_OK, path=None, extlist=[]):
    """
    Locate a file in the user's standard path, or a supplied path. The function
    yields full paths in which the given file matches a file in a directory on
    the path. it uses extlist (a list of extensions) and the PATHEXT Variable 
    (used on windows) to check for file+ extension
    """
    if not path:
        path = os.environ.get("PATH", os.defpath)
    exts = extlist+ filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))

    for dir in path.split(os.pathsep):
        full_path = os.path.join(dir, file)
        if os.path.exists(full_path) and os.access(full_path, mode):
            yield full_path
        for ext in exts:
            full_ext = full_path + ext
            if os.path.exists(full_ext) and os.access(full_ext, mode):
                yield full_ext

def tempfilecopy(filelike, tmp_dir=None, mkdir=False, **kwargs):
    if mkdir and not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    with tempfile.NamedTemporaryFile(delete=False, dir=tmp_dir, **kwargs) as outputfile:
        outputfilename = outputfile.name
        outputfile.write(filelike.read())
    return outputfilename


def which_path(setting, *args, **kwargs):
    if hasattr(settings, setting):
        return getattr(settings, setting)
    else:
        return which(*args, **kwargs).next()
