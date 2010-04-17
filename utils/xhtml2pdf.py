import subprocess
import killableprocess
import tempfile

def xhtml2pdf(html, **options):
    """ 
    Calls `xhtml2pdf` from pisa.
    All `xhtml2pdf` commandline options (see `man htmldoc`) are supported, just replace '-' with '_' and use True/False values 
    for options without arguments.
    """
    args = ['xhtml2pdf']
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
    with tempfile.NamedTemporaryFile(prefix="xhtml2pdfdebug", delete=False) as t:
        t.write(str(args))
        popen = killableprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, stderr = popen.communicate(html)
        t.write(stderr)
    return result 
