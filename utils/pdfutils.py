import subprocess
import os
from StringIO import StringIO
from django.template import Context, loader
import tempfile

def stamp_pdf(filename, barcode_content):
    template = loader.get_template('xhtml2pdf/barcode.ps')
    barcode_ps = template.render(Context({'barcode': barcode_content}))
    
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(barcode_ps)
        tmp.flush()
        tmp.seek(0)
        
        tmp_out = tempfile.NamedTemporaryFile(suffix='.pdf')
        
        print 'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=- %s | pdftk %s stamp - output %s' % (tmp.name, filename, tmp_out.name)
        rofl = subprocess.Popen('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=- %s | pdftk %s stamp - output %s' % (tmp.name, filename, tmp_out.name), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        pdf, err = rofl.communicate()
        print '\n'
        print err
    
    if rofl.returncode != 0:
        raise ValueError('pdftk returned with errorcode %s' % rofl.returncode)
    
    print '\n\n\nYAYZ\n\n\n'
    
    return tmp_out


