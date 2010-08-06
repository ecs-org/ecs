import os, sys
import subprocess
from subprocess import PIPE, STDOUT
import killableprocess
import tempfile
import time
from StringIO import StringIO

from pdfminer.pdfparser import PDFParser, PDFDocument

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

def pdf_isvalid(filelike):
    filelike.seek(0)
    parser = PDFParser(filelike)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    if not doc.is_extractable:
        return False
    filelike.seek(0)
    return True
    
def pdf_pages(filelike):
    filelike.seek(0)
    parser = PDFParser(filelike)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    # TODO: is hack
    pages = 0
    for page in doc.get_pages():
        pages += 1
    filelike.seek(0)
    return pages
    
def pdf_barcodestamp(source_filelike, barcode_content, dest_filelike):
    '''
    takes source pdf, stamps a barcode into it and output it to dest
    raises IOError if something goes wrong (including exit errorcode and stderr output attached)
    '''
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode_content})) # render barcode template to ready to use postscript file
    
    try:
        barcode_pdf_oshandle, barcode_pdf_name = tempfile.mkstemp(suffix='.pdf') 
        # render barcode postscript file to pdf
        gs = subprocess.Popen([ghostscript(), 
            '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dAutoRotatePages=/None', 
            '-sOutputFile=%s' % barcode_pdf_name, '-c', '<</Orientation 0>> setpagedevice', '-'],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        gsresult = gs.communicate(barcode_ps)
        if gs.returncode != 0:
            raise IOError('ghostscript returned error code %n , stderr: ' % gs.returncode, gsresult[1])        
    finally:    
        os.close(barcode_pdf_oshandle)
        
    source_filelike.seek(0)
    # implant barcode pdf to source pdf on every page 
    pdftk = subprocess.Popen([which('pdftk').next(),
        '-', 'stamp', barcode_pdf_name, 'output', '-', 'dont_ask'],
        bufsize=-1, stdin=source_filelike, stdout=dest_filelike, stderr=PIPE)       
    pdftkresult = pdftk.communicate()
    #print pdftkresult, pdftk.returncode, target_name
    source_filelike.seek(0)
    if pdftk.returncode != 0:
        raise IOError('stamping pipeline returned with errorcode %n , stderr: ' % pdftk.returncode, pdftkresult[1])
    
    if os.path.isfile(barcode_pdf_name):
        os.remove(barcode_pdf_name)

"""
        if destdir:
            dir=os.path.abspath(destdir)
            if not os.path.exists(dir):
                os.makedirs(dir)
            target_oshandle, target_name = tempfile.mkstemp(dir=dir, suffix='.pdf')
        else:
            target_oshandle, target_name = tempfile.mkstemp(suffix='.pdf')
"""
	
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
