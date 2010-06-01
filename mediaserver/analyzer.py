import cStringIO
import pyPdf


class Analyzer(object):
    def sniff(self, pdf_name):
        self.valid = False
        self.pages = 0

        with open(pdf_name, 'r') as f:
            pdf_data = f.read()

        pdf_data = str(pdf_data)

        try:
            pdf = pyPdf.PdfFileReader(cStringIO.StringIO(pdf_data))
        except:
            print 'error reading pdf file "%s"' % pdf_name
            return

        if pdf:
            self.valid = True
            self.pages = pdf.getNumPages()




