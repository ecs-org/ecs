import os, sys
import subprocess
import tempfile
import time

from django.template import Context, loader
from django.core.files import File
from django.conf import settings

from pdfminer.pdfparser import PDFParser, PDFDocument

import ecs.utils.killableprocess 
from ecs.utils.pathutils import which


def ghostscript():
    '''
    returns ghostscript executable, checks ECS_GHOSTSCRIPT and uses it if exists
    '''
    return settings.ECS_GHOSTSCRIPT if hasattr(settings,"ECS_GHOSTSCRIPT") else which('gs').next()

        
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
    pages = sum(1 for _ in doc.get_pages())
    filelike.seek(0)
    return pages


def pdf2png(inputfile, outputnaming, pixelwidth=None, first_page=None, last_page=None):
    """
    takes inputfile and renders it to a set of png files, optional specify pixelwidth, first_page, last_page
    raises IOError(descriptive text, returncode, stderr) in case of failure
    outputnameing follows ghostscript conventions. The general form supported is:
    "%[flags][width][.precision][l]type", flags is one of: "#+-", type is one of: "diuoxX"
    For more information, please refer to documentation on the C printf format specifications.
    """

    cmd = [ ghostscript(), '-dQUIET', '-dSAFER', '-dBATCH', '-dNOPAUSE',
        '-sDEVICE=png16m', '-dGraphicsAlphaBits=4', '-dTextAlphaBits=4', '-dPDFFitPage',  '-sPAPERSIZE=a4']
    cm_per_inch = 2.54; din_a4_x = 21.0; din_a4_y = 29.7
    
    if pixelwidth:
        dpix = pixelwidth / (din_a4_x / cm_per_inch)
        cmd += ['-r%.5f' % (dpix)]
    if first_page:
        cmd += ['-dFirstPage=%s' % first_page]
    if last_page:
        cmd += ['-dLastPage=%s' % last_page]
    cmd += ['-sOutputFile='+ namingtemplate, sourcefile]

    popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode != 0:
        raise IOError('pdf2png processing using ghostscript returned error code %i , stderr: %s' % (popen.returncode, stderr))        
    
    
def pdf_barcodestamp(source_filelike, dest_filelike, barcode1, barcode2=None, timeoutseconds=30):
    '''
    takes source pdf, stamps a barcode into it and output it to dest
    raises IOError if something goes wrong (including exit errorcode and stderr output attached)
    '''
    if barcode2:
        raise(NotImplementedError)
        # TODO: barcode2_content is currently unimplemented
        
    # render barcode template to ready to use postscript file
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode1})) 
    
    try:
        # render barcode postscript file to pdf
        barcode_pdf_oshandle, barcode_pdf_name = tempfile.mkstemp(suffix='.pdf') 
        cmd = [ghostscript(), 
            '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dAutoRotatePages=/None', 
            '-sOutputFile=%s' % barcode_pdf_name, '-c', '<</Orientation 0>> setpagedevice', '-']
        popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate(barcode_ps)
        if popen.returncode != 0:
            raise IOError('barcode processing using ghostscript returned error code %i , stderr: %s' % (popen.returncode, stderr))        
    finally:    
        os.close(barcode_pdf_oshandle)
    
    # implant barcode pdf to source pdf on every page 
    source_filelike.seek(0)
    cmd = [which('pdftk').next(), '-', 'stamp', barcode_pdf_name, 'output', '-', 'dont_ask']
    popen = subprocess.Popen(cmd, bufsize=-1, stdin=source_filelike, stdout=dest_filelike, stderr=subprocess.PIPE)       
    stdout, stderr = popen.communicate()
    source_filelike.seek(0)
    if os.path.isfile(barcode_pdf_name):
        os.remove(barcode_pdf_name)
    if popen.returncode != 0:
        raise IOError('stamping pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))
  
  
def pdftotext(pdffilename, pagenr=None, timeoutseconds= 30):
    """
    Calls `pdftotext` from the commandline, takes a pdffilename that must exist on the local filesystem and returns extracted text
    if pagenr is set only Page pagenr is extracted; Raises IOError if something went wrong
    """
    cmd = ["pdftotext", "-raw", "-nopgbrk", "-enc", "UTF-8", "-eol", "unix", "-q"]
    if pagenr:
        cmd += ["-f", "%s" % pagenr,  "-l",  "%s" % pagenr]
    cmd += [pdffilename, "-"]
    popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode != 0:
        raise IOError('pdftotext pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))
    return stdout

    
def xhtml2pdf(html, timeoutseconds=30):
    """ 
    Calls pisa `xhtml2pdf` from the commandline, takes xhtml with embedded css and returns pdf
    Raises IOError (descriptive text, returncode, stderr) in case something went wrong
    """
    if isinstance(html, unicode):
        html = html.encode("utf-8")
    cmd = [which('xhtml2pdf').next(), '-q', '-', '-']
  
    with tempfile.NamedTemporaryFile() as t:
        t.write(html); t.flush(); t.seek(0)
        popen = ecs.utils.killableprocess.Popen(cmd, stdin=t, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            raise IOError('xhtml2pdf pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))
    return stdout 
