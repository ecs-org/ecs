'''
========
pdfutils
========

- identification (is valid pdf, number of pages), 
- manipulation (barcode stamp)
- conversion (to PDF/A, to text)
- creation (from html)

'''
import os, subprocess, logging, shutil
from binascii import hexlify
from tempfile import TemporaryFile, NamedTemporaryFile, mkdtemp

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_bytes


logger = logging.getLogger(__name__)


def pdf_barcodestamp(source, barcode, text=None):
    ''' takes source pdf, stamps a barcode onto every page and output it to dest
    
    :raise IOError: if something goes wrong (including exit errorcode and stderr output attached)
    ''' 
    barcode_ps = loader.render_to_string('pdf/barcode.ps') + """
        gsave 
        20 100 moveto 0.5 0.5 scale 0 rotate
        ({}) () /qrcode /uk.co.terryburton.bwipp findresource exec
        grestore
    """.format(barcode)

    if text:
        barcode_ps += '''
            gsave

            % Define the HelveticaLatin1 font, which is like Helvetica, but
            % using the ISOLatin1Encoding encoding vector.
            /Helvetica findfont
            dup length dict
            begin
                {{def}} forall
                /Encoding ISOLatin1Encoding def
                currentdict
            end
            /HelveticaLatin1 exch definefont

            /HelveticaLatin1 6 selectfont
            <{}> dup stringwidth pop 132 add 32 exch moveto
            270 rotate show
            grestore
        '''.format(hexlify(text.encode('latin-1', 'replace')).decode('ascii'))

    with NamedTemporaryFile() as pdf:
        p = subprocess.Popen([
            'gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite',
            '-sPAPERSIZE=a4', '-dAutoRotatePages=/None', '-sOutputFile=-', '-c',
            '<</Orientation 0>> setpagedevice', '-'
        ], stdin=subprocess.PIPE, stdout=pdf, stderr=subprocess.PIPE)
        p.stdin.write(barcode_ps.encode('ascii'))
        p.stdin.close()
        if p.wait():
            raise subprocess.CalledProcessError(p.returncode, 'ghostscript')

        stamped = TemporaryFile()
        p = subprocess.check_call(
            ['pdftk', '-', 'stamp', pdf.name, 'output', '-', 'dont_ask'],
            stdin=source, stdout=stamped
        )

    stamped.seek(0)
    return stamped
    
  
def decrypt_pdf(src):
    decrypted = TemporaryFile()
    popen = subprocess.Popen(['qpdf', '--decrypt', '/dev/stdin', '-'],
        stdin=src, stdout=decrypted, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode in (0, 3):  # 0 == ok, 3 == warning
        if popen.returncode == 3:
            logger.warn('qpdf warning:\n%s', smart_bytes(stderr, errors='backslashreplace'))
    else:
        from ecs.users.utils import get_current_user
        user = get_current_user()
        logger.warn('qpdf error (returncode=%s):\nUser: %s (%s)\n%s', popen.returncode, user, user.email if user else 'anonymous', smart_bytes(stderr, errors='backslashreplace'))
        raise ValueError('pdf broken')
    decrypted.seek(0)
    return decrypted


def wkhtml2pdf(html, header_html=None, footer_html=None, param_list=None):
    ''' Takes html and makes an pdf document out of it using the webkit engine
    '''
    if isinstance(html, str): 
        html = html.encode('utf-8') 
    if isinstance(header_html, str):
        header_html = header_html.encode('utf-8')
    if isinstance(footer_html, str):
        footer_html = footer_html.encode('utf-8')
    
    cmd = ['wkhtmltopdf-amd64',
        '--margin-left', '2cm',
        '--margin-top', '2cm',
        '--margin-right', '2cm',
        '--margin-bottom', '2cm',
        '--page-size', 'A4',
    ] + getattr(settings, 'WKHTMLTOPDF_OPTIONS', [])
    tmp_dir = mkdtemp()
    shutil.copytree(os.path.join(settings.PROJECT_DIR, 'ecs', 'utils', 'pdf'), os.path.join(tmp_dir, 'media'))

    if header_html:
        header_html_file = NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
        header_html_file.write(header_html)
        header_html_file.close()
        cmd += ['--header-html', header_html_file.name]
    if footer_html and not getattr(settings, 'DISABLE_WKHTML2PDF_FOOTERS', False):
        footer_html_file = NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
        footer_html_file.write(footer_html)
        footer_html_file.close()
        cmd += ['--footer-html', footer_html_file.name]

    if param_list:
        cmd += param_list

    html_file = NamedTemporaryFile(suffix='.html', dir=tmp_dir, delete=False)
    html_file.write(html)
    html_file.close()
    cmd += ['page', html_file.name]

    pdf_file = NamedTemporaryFile(suffix='.pdf', dir=tmp_dir, delete=False)
    pdf_file.close()
    cmd += [pdf_file.name]
    
    try:
        popen = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate() 
        if popen.returncode != 0: 
            raise IOError('wkhtmltopdf pipeline returned with errorcode %i , stderr: %s' % (popen.returncode, stderr))

        with open(pdf_file.name, 'rb') as pdf:
            ret = pdf.read()

    finally:
        shutil.rmtree(tmp_dir)

    return ret
