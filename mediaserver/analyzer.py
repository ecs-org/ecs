import pyPdf


class Analyzer(object):
    def sniff(self, pdf_name):
        self.valid = False
        self.pages = 0
        try:
            f = file(pdf_name, 'r')
            pdf = pyPdf.PdfFileReader(f)
        except:
            print 'error reading pdf file "%s"' % pdf_name
            return

        if pdf:
            self.valid = True
            self.pages = pdf.getNumPages()




