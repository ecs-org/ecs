import subprocess
import killableprocess
import tempfile
import os, sys
import time

def which(file, mode=os.F_OK | os.X_OK, path=None):
    """Locate a file in the user's path, or a supplied path. The function
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

                
def xhtml2pdf(html, **options):
    """ 
    Calls `xhtml2pdf` from pisa.
    All `xhtml2pdf` commandline options (see `man htmldoc`) are supported, just replace '-' with '_' and use True/False values 
    for options without arguments.
    """
    if isinstance(html, unicode):
        html = html.encode("utf-8")
    if sys.platform.startswith("linux"): # ugly, but our production platform is Ubuntu
        cmd = 'ulimit -t 30 ; ' # FIXME: Hardcoded process abbort criterium: Currently 30 Seconds
    else:
        cmd = ''
    cmd += which('xhtml2pdf').next()
    args = [cmd, '-q']
    for key, value in options.iteritems():
        if value is False:
            continue
        option = "--%s" % key.replace('_', '-')
        args.append(option)
        if value is not True:
            args.append(str(value))
    args.append('-')
    args.append('-')

    # FIXME: add error handling / sanitize options
    # FIXME: debug file is left on disk 
    with tempfile.NamedTemporaryFile(prefix=time.strftime("xhtml2pdfdebug-%y%m%d%H%M%S-"), delete=False) as t:
        t.write(str(args) + "\n")
        t.write(str(os.environ.get("PATH", os.defpath)) + "\n\n")
        with open(t.name + ".html", "w") as html_out:
            html_out.write(html)
        t.flush()
        popen = killableprocess.Popen(" ".join(args), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=t)
        result, stderr = popen.communicate(html)
    return result 
