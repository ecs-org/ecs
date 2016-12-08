'''
========
pdfutils
========

- identification (is valid pdf, number of pages),
- manipulation (barcode stamp)
- conversion (to PDF/A, to text)
- creation (from html)

'''
import os
import mimetypes
import subprocess, logging
from binascii import hexlify
from tempfile import TemporaryFile, NamedTemporaryFile

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_bytes

from weasyprint import HTML, default_url_fetcher


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


def html2pdf(html, param_list=None):
    ''' Takes html and makes an pdf document out of it
    '''
    if isinstance(html, str):
        html = html.encode('utf-8')

    def _url_fetcher(url):
        if url.startswith('static:'):
            path = os.path.abspath(os.path.join(
                settings.STATIC_ROOT, url[len('static:'):]))
            if not path.startswith(settings.STATIC_ROOT):
                raise IOError()
            with open(path, 'rb') as f:
                data = f.read()
            return {'string': data, 'mime_type': mimetypes.guess_type(path)[0]}

        return default_url_fetcher(url)

    return HTML(string=html, url_fetcher=_url_fetcher).write_pdf()
