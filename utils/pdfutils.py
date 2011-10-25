# -*- coding: utf-8 -*-
'''
========
pdfutils
========

- identification (is valid pdf, number of pages), 
- manipulation (barcode stamp)
- conversion (to PDF/A, to text, to png)
- creation (from html)

'''
import os, subprocess, tempfile, logging, copy, shutil
from cStringIO import StringIO

from django.conf import settings
from django.template import Context, loader

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import PDFException

from ecs.utils.pathutils import which

MONTAGE_PATH = which('montage').next()
GHOSTSCRIPT_PATH =  settings.ECS_GHOSTSCRIPT if hasattr(settings,"ECS_GHOSTSCRIPT") else which('gs').next()
WKHTMLTOPDF_PATH =  settings.ECS_WKHTMLTOPDF if hasattr(settings,"ECS_WKHTMLTOPDF") else which('wkhtmltopdf', extlist=["-amd64", "-i386"]).next()
 
PDF_MAGIC = r"%PDF-"


class Page(object):
    ''' Properties of a image of an page of an pageable media (id, tiles_x, tiles_y, width, pagenr)
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
    
    :param filelike: filelike object, seekable
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


def pdf_barcodestamp(source_filelike, dest_filelike, barcode1, barcode2=None, barcodetype="qrcode", timeoutseconds=30):
    ''' takes source pdf, stamps a barcode into it and output it to dest
    
    :raise IOError: if something goes wrong (including exit errorcode and stderr output attached)
    ''' 
    S_BARCODE_TEMPLATE = """
        gsave 
        {{ moveto }} moveto {{ scale }} scale {{ rotate }} rotate
        ({{ header }}{{ barcode }}) ({{options}}) /{{barcodetype}} /uk.co.terryburton.bwipp findresource exec
        grestore
        """
    D_CODE128 = {'moveto': '50 600', 'scale': '0.5 0.5', 'rotate': '89.999', 
        'header': '^104', 'options': 'includetext', 'barcodetype': "code128",
        }
    D_QRCODE =  {'moveto': '20 100', 'scale': '0.5 0.5', 'rotate': '0', 
        'header': '', 'options': '', 'barcodetype': "qrcode",
        }
    barcode1dict = copy.deepcopy(D_QRCODE)
    barcode1dict['barcode']= barcode1
    barcode1s = loader.get_template_from_string(S_BARCODE_TEMPLATE).render(Context(barcode1dict))
      
    if barcode2:
        barcode2dict = copy.deepcopy(D_QRCODE)
        barcode2dict['moveto'] = '20 600'
        barcode2dict['barcode'] =  barcode2
        barcode2s = loader.get_template_from_string(S_BARCODE_TEMPLATE).render(Context(barcode2dict))
    else:
        barcode2s = ""
    
    # render barcode template to ready to use postscript file
    template = loader.get_template_from_string("""{{barcode1}}{{barcode2}}""")
    barcode_ps = loader.render_to_string('wkhtml2pdf/barcode.ps')+ template.render(Context({
        'barcode1': barcode1s, 'barcode2': barcode2s,}))
    
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
    ''' Extract Text from an pdf, you can extract the whole text, or only text from one page of an document. 
    
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
    
    :return: iterator yielding tuples of Page(id, tiles_x, tiles_y, width, pagenr), filelike
    :raise IOError: ghostscript/montage conversion error 
    :attention: you should close returned filelike objects if they have a .close() method after usage
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
    ''' converts a pdf file into a PDF/A 1b file
    '''
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
        '-dSubsetFonts=false',
        '-sProcessColorModel=DeviceCMYK',
        '-sDEVICE=pdfwrite',
        '-dPDFACompatibilityPolicy=1',
        '-sOutputFile=%stdout',
        'PDFA_def.ps',
        '-',
    ]

    if not hasattr(real_infile, 'fileno'):
        infile = tempfile.TemporaryFile(dir=settings.TEMPFILE_DIR)
        infile.write(real_infile.read())
        infile.seek(0)
    else:
        infile = real_infile

    if not hasattr(real_outfile, 'fileno'):
        outfile = tempfile.TemporaryFile(dir=settings.TEMPFILE_DIR)
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


def wkhtml2pdf(html, header_html=None, footer_html=None, param_list=None):
    ''' Takes html and makes an pdf document out of it using the webkit engine
    '''
    
    if isinstance(html, unicode): 
        html = html.encode('utf-8') 
    if isinstance(header_html, unicode):
        header_html = header_html.encode('utf-8')
    if isinstance(footer_html, unicode):
        footer_html = footer_html.encode('utf-8')
    
    cmd = [WKHTMLTOPDF_PATH,
        '--margin-left', '2cm',
        '--margin-top', '2cm',
        '--margin-right', '2cm',
        '--margin-bottom', '2cm',
        '--page-size', 'A4',
        '--zoom', '1',
    ]

    tmp_dir = tempfile.mkdtemp(dir=settings.TEMPFILE_DIR)
    shutil.copytree(os.path.join(settings.PROJECT_DIR, 'utils', 'pdf'), os.path.join(tmp_dir, 'media'))

    if header_html:
        header_html_file = tempfile.NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
        header_html_file.write(header_html)
        header_html_file.close()
        cmd += ['--header-html', header_html_file.name]
    if footer_html:
        footer_html_file = tempfile.NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
        footer_html_file.write(footer_html)
        footer_html_file.close()
        cmd += ['--footer-html', footer_html_file.name]

    if param_list:
        cmd += param_list

    html_file = tempfile.NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
    html_file.write(html)
    html_file.close()
    cmd += ['page', html_file.name]

    pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', dir=tmp_dir, delete=False)
    pdf_file.close()
    cmd += [pdf_file.name]

    try:
        popen = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate() 
        if popen.returncode != 0: 
            raise IOError('wkhtmltopdf pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))             

        pdfa = StringIO() 
        with open(pdf_file.name, 'rb') as pdf:
            pdf2pdfa(pdf, pdfa)
        pdfa.seek(0)
        ret = pdfa.getvalue()
        pdfa.close()

    finally:
        shutil.rmtree(tmp_dir)

    return ret
