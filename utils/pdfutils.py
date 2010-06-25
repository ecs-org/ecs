import subprocess
import os
from StringIO import StringIO
from django.template import Context, loader
import tempfile

from django.core.files import File

from ecs.utils.xhtml2pdf import which


def stamp_pdf(filename, barcode_content):
    # FIXME: remove tempfile foo
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode_content}))
    
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(barcode_ps)
        tmp.flush()
        tmp.seek(0)
        
        tmp_out = tempfile.NamedTemporaryFile(suffix='.pdf')
        
        gs = subprocess.Popen([which('gs').next(), '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sPAPERSIZE=a4', '-dAutoRotatePages=/None', '-sOutputFile=-', '-c', '<</Orientation 0>> setpagedevice', '-f', tmp.name], stdout=subprocess.PIPE)
        
        pdftk = subprocess.Popen([which('pdftk').next(), filename, 'stamp', '-', 'output', tmp_out.name], stdin=gs.stdout)
        
        pdftk.wait()
    
    if pdftk.returncode != 0:
        raise ValueError('pdftk returned with errorcode %s' % pdftk.returncode)
    
    return File(tmp_out)


