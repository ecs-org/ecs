# -*- coding: utf-8 -*-

import os, subprocess, tempfile, binascii, logging
from cStringIO import StringIO

from django.conf import settings
from django.template import Context, loader
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import PDFException

import ecs.utils.killableprocess 
from ecs.utils.pathutils import which

MONTAGE_PATH = which('montage').next()
GHOSTSCRIPT_PATH =  settings.ECS_GHOSTSCRIPT if hasattr(settings,"ECS_GHOSTSCRIPT") else which('gs').next()
PDF_MAGIC = r"%PDF-"


class Page(object):
    '''
    Properties of a image of an page of an pageable media (id, tiles_x, tiles_y, width, pagenr)
    '''
    def __init__(self, id, tiles_x, tiles_y, width, pagenr):
        self.id = id
        self.tiles_x = tiles_x
        self.tiles_y = tiles_y
        self.width = width
        self.pagenr = pagenr

    def __repr__(self):
        return str("%s_%s_%sx%s_%s" % (self.id, self.width, self.tiles_x, self.tiles_y , self.pagenr))

        
def pdf_isvalid(filelike):
    ''' returns True if valid pdf, else False
    @param filelike: filelike object, seekable
    '''
    logger = logging.getLogger()
    isvalid = False    
    filelike.seek(0)  
    
    if filelike.read(len(PDF_MAGIC)) != PDF_MAGIC:
        return False
    else:
        filelike.seek(0)
    try:
        parser = PDFParser(filelike)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        if doc.is_extractable:
            isvalid = True
    except PDFException as excobj:
        logger.warning("pdf has valid header but, still not valid pdf, exception was %r" %(excobj))
        isvalid = False
            
    filelike.seek(0)
    return isvalid
    
    
def pdf_page_count(filelike):
    ''' returns number of pages of an pdf document '''
    filelike.seek(0)
    parser = PDFParser(filelike)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    pages = sum(1 for _ in doc.get_pages())
    filelike.seek(0)
    return pages


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
        cmd = [GHOSTSCRIPT_PATH, 
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

  
def pdf2text(pdffilename, pagenr=None, timeoutseconds= 30):
    '''
    Extract Text from an pdf, you can extract the whole text, or only text from one page of an document. 
    Calls `pdftotext` from the commandline, takes a pdffilename that must exist on the local filesystem and returns extracted text
    if pagenr is set only Page pagenr is extracted; Raises IOError if something went wrong
    '''
    cmd = ["pdftotext", "-raw", "-nopgbrk", "-enc", "UTF-8", "-eol", "unix", "-q"]
    if pagenr:
        cmd += ["-f", "%s" % pagenr,  "-l",  "%s" % pagenr]
    cmd += [pdffilename, "-"]
    popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode != 0:
        raise IOError('pdftotext pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))
    return stdout


def pdf2pngs(id, source_filename, render_dirname, width, tiles_x, tiles_y, aspect_ratio, dpi, depth):
    ''' renders a pdf to multiple png pictures placed in render_dirname
    @return: iterator yielding tuples of Page(id, tiles_x, tiles_y, width, pagenr), filelike
    @raise IOError: ghostscript/montage conversion error 
    @attention: you should close returned filelike objects if they have a .close() method after usage
    '''
    margin_x = 0
    margin_y = 0   
    height = width * aspect_ratio
    tile_width = (width / tiles_x) - margin_x
    tile_height = (height / tiles_y) - margin_y
    tmp_dir_prefix = os.path.join(render_dirname, "%s_%sx%s" % (width, tiles_x, tiles_y))
    os.mkdir(tmp_dir_prefix)
    tmp_page_prefix = os.path.join(tmp_dir_prefix, '%s_%s_%sx%s_' % (id, width, tiles_x, tiles_y)) + "%04d"
     
    args = [MONTAGE_PATH, "-verbose", "-geometry", "%dx%d+%d+%d" % (tile_width, tile_height, margin_x, margin_y),
        "-tile", "%dx%d" % (tiles_x, tiles_y), "-density", "%d" % dpi, "-depth", "%d" % depth,
        source_filename, "PNG:%s" % tmp_page_prefix]
    
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        raise IOError('montage returned error code:%d %s' % (returncode, stdout))

    pagenr = 0
    for ds in sorted(os.listdir(tmp_dir_prefix)):
        dspath = os.path.join(tmp_dir_prefix, ds)
        pagenr += 1
        yield Page(id, tiles_x, tiles_y, width, pagenr), open(dspath,"rb")

def pdf2pdfa(real_infile, real_outfile):
    workdir = os.path.join(settings.PROJECT_DIR, 'utils', 'pdfa')

    gs = [GHOSTSCRIPT_PATH,
        '-q',
        '-dPDFA',
        '-dBATCH',
        '-dNOPAUSE',
        '-dNOOUTERSAVE',
        '-dUseCIEColor',
        '-dSAFER',
        '-dNOPLATFONTS',
        '-dEmbedAllFonts=true',
        '-dSubsetFonts=true',
        '-sProcessColorModel=DeviceCMYK',
        '-sDEVICE=pdfwrite',
        '-dPDFACompatibilityPolicy=1',
        '-sOutputFile=%stdout',
        'PDFA_def.ps',
        '-',
    ]

    if not hasattr(real_infile, 'fileno'):
        infile = tempfile.TemporaryFile()
        infile.write(real_infile.read())
        infile.seek(0)
    else:
        infile = real_infile

    if not hasattr(real_outfile, 'fileno'):
        outfile = tempfile.TemporaryFile()
    else:
        outfile = real_outfile

    offset = real_outfile.tell()

    try:
        p = subprocess.Popen(gs, cwd=workdir, stdin=infile, stdout=outfile, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise IOError('gs pipeline returned with errorcode %i , stderr: %s' % (p.returncode, stderr))
    finally:
        if not hasattr(real_infile, 'fileno'):
            infile.close()
        if not hasattr(real_outfile, 'fileno'):
            outfile.seek(0)
            real_outfile.write(outfile.read())
            outfile.close()

    return real_outfile.tell() - offset

def xhtml2pdf(html, timeoutseconds=30):
    '''
    Takes custom (pisa style) xhtml and makes an pdf document out of it
    Calls pisa `xhtml2pdf` from the commandline, takes xhtml with embedded css and returns pdf
    Raises IOError (descriptive text, returncode, stderr) in case something went wrong
    '''
    if isinstance(html, unicode):
        html = html.encode("utf-8")
    cmd = [which('xhtml2pdf').next(), '-q', '-', '-']
  
    with tempfile.NamedTemporaryFile() as t:
        t.write(html); t.flush(); t.seek(0)
        popen = ecs.utils.killableprocess.Popen(cmd, stdin=t, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            raise IOError('xhtml2pdf pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))

    pdf = StringIO(stdout)
    pdfa = StringIO()

    try:
        pdf2pdfa(pdf, pdfa)
        ret = pdfa.getvalue()
    finally:
        pdf.close()
        pdfa.close()

    return ret


"""
def pdf2png(inputfile, outputnaming, pixelwidth=None, first_page=None, last_page=None):
    takes inputfile and renders it to a set of png files, optional specify pixelwidth, first_page, last_page
    raises IOError(descriptive text, returncode, stderr) in case of failure
    outputnameing follows ghostscript conventions. The general form supported is:
    "%[flags][width][.precision][l]type", flags is one of: "#+-", type is one of: "diuoxX"
    For more information, please refer to documentation on the C printf format specifications.

    cmd = [ GHOSTSCRIPT_PATH, '-dQUIET', '-dSAFER', '-dBATCH', '-dNOPAUSE',
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
"""

