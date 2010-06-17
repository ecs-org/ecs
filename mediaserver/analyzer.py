# -*- coding: utf-8 -*-

import pyPdf


class Analyzer(object):
    def sniff(self, pdf_name):
        f = file(pdf_name, 'r')
        self.sniff_file(f)

    def sniff_file(self, f):
        self.valid = False
        self.pages = 0
        try:
            pdf = pyPdf.PdfFileReader(f)
        except:
            print 'analyzer: error reading pdf file "%s"' % f.name
            return
        if pdf:
            self.valid = True
            self.pages = pdf.getNumPages()




