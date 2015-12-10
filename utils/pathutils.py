# -*- coding: utf-8 -*-
import os

from django.conf import settings


def which(file, mode=os.F_OK | os.X_OK, path=None, extlist=[]):
    """
    Locate a file in the user's standard path, or a supplied path. The function
    yields full paths in which the given file matches a file in a directory on
    the path. it uses extlist (a list of extensions) to check for file+ extension
    """
    if not path:
        path = os.environ.get("PATH", os.defpath)

    for dir in path.split(os.pathsep):
        full_path = os.path.join(dir, file)
        if os.path.exists(full_path) and os.access(full_path, mode):
            yield full_path
        for ext in extlist:
            full_ext = full_path + ext
            if os.path.exists(full_ext) and os.access(full_ext, mode):
                yield full_ext

def which_path(setting, *args, **kwargs):
    path = getattr(settings, setting, None)
    if path is None:
        path = which(*args, **kwargs).next()
    return path
