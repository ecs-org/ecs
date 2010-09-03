'''
Created on Aug 29, 2010

@author: elchaschab
'''

from django import forms

class PdfUploadForm(forms.Form):
    pdffile  = forms.FileField()