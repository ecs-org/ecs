import subprocess
import os
from StringIO import StringIO
from django.template import Context, loader
import tempfile

def stamp_pdf(filename, barcode_content):
    # FIXME: remove tempfile foo
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode_content}))
    
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(barcode_ps)
        tmp.flush()
        tmp.seek(0)
        
        tmp_out = tempfile.NamedTemporaryFile(suffix='.pdf')
        
        p = subprocess.Popen('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dAutoRotatePages=/None -sOutputFile=- -c "<</Orientation 0>> setpagedevice"  -f %s | pdftk %s stamp - output %s' % (tmp.name, filename, tmp_out.name), shell=True)
        p.wait()
    
    if p.returncode != 0:
        raise ValueError('pdftk returned with errorcode %s' % p.returncode)
    
    return tmp_out


