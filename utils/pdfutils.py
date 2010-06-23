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
        
        #s = subprocess.Popen(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-sOutputFile=-', tmp.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #pdftk = subprocess.Popen(['pdftk', filename, 'stamp', '-', 'output', '-'], stdin=gs.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #pdftk = subprocess.Popen(['cat', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #pdf, err = pdftk.communicate()
        #print '\n', pdf, err, '\n'
        
        print 'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=- %s|pdftk %s stamp - output -' % (tmp.name, filename)
        rofl = subprocess.Popen('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=- %s|pdftk %s stamp - output -' % (tmp.name, filename), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        pdf, err = rofl.communicate()
        print '\n'
        print pdf
        print err
        print '\n'
    
    if rofl.returncode != 0:
        raise ValueError('pdftk returned with errorcode %s' % rofl.returncode)
    
    print '\n\n\nYAYZ\n\n\n'
    
    return StringIO(pdf)


