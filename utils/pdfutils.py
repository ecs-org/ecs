import os, sys
import subprocess
import killableprocess
import tempfile
import time
from StringIO import StringIO

from django.template import Context, loader
from django.core.files import File
from django.conf import settings

from ecs.utils.pathutils import which

def ghostscript():
    '''
    returns ghostscript executable, checks ECS_GHOSTSCRIPT and uses it if exists
    '''
    if hasattr(settings,"ECS_GHOSTSCRIPT"):
        return settings.ECS_GHOSTSCRIPT
    else:
        return which('gs').next()

def stamp_pdf(filename, barcode_content):
    # FIXME: remove tempfile foo
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode_content}))
    
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(barcode_ps)
        tmp.flush()
        tmp.seek(0)
        tmp_out = tempfile.NamedTemporaryFile(suffix='.pdf')
        
        gs = subprocess.Popen([ghostscript(), '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dAutoRotatePages=/None', '-sOutputFile=-', '-c', '<</Orientation 0>> setpagedevice', '-f', tmp.name], stdout=subprocess.PIPE)
        pdftk = subprocess.Popen([which('pdftk').next(), filename, 'stamp', '-', 'output', tmp_out.name], stdin=gs.stdout)       
        pdftk.wait()
    
    if pdftk.returncode != 0:
        raise ValueError('pdftk returned with errorcode %s' % pdftk.returncode)
    
    return File(tmp_out)


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
        if popen.returncode:
            print result, stderr
    return result 
