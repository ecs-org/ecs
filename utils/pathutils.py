# -*- coding: utf-8 -*-

import os
import tempfile

def which(file, mode=os.F_OK | os.X_OK, path=None):
    """
    Locate a file in the user's standard path, or a supplied path. The function
    yields full paths in which the given file matches a file in a directory on
    the path. on windows it uses the PATHEXT Variable to check for file+ extension
    """
    if not path:
        path = os.environ.get("PATH", os.defpath)
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))

    for dir in path.split(os.pathsep):
        full_path = os.path.join(dir, file)
        if os.path.exists(full_path) and os.access(full_path, mode):
            yield full_path
        for ext in exts:
            full_ext = full_path + ext
            if os.path.exists(full_ext) and os.access(full_ext, mode):
                yield full_ext

def tempfilecopy(filelike):
    with tempfile.NamedTemporaryFile(delete=False) as outputfile:
        outputfilename = outputfile.name
        outputfile.write(filelike.read())
    return outputfilename
