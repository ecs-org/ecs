'''
Created on Sep 3, 2010

@author: elchaschab
'''
import mimetypes
import time
from uuid import uuid4
from django.db import models
from ecs.utils.pdfutils import pdf_isvalid, pdf_pages
from django.core.exceptions import ValidationError
import hashlib

    
class PdfDocumentModel(models.Model):
    uuid = models.SlugField(max_length=36)
    hash = models.SlugField(max_length=32)
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    pages = models.IntegerField(null=True, blank=True)
    lastaccess = models.DateTimeField()
    
    class Meta:
        app_label = 'mediaserver'
    
    def save(self, filelike, **kwargs):
        if not pdf_isvalid(self.file):
            raise ValidationError("Invalid Pdf")

        if not self.uuid_document:
            self.uuid = str(uuid4())

        if not self.lastaccess:
            self.lastaccess = time.time()
        
        if not self.pages:    
            self.pages = pdf_pages(filelike)
        
        if not self.hash:
            m = hashlib.md5() # calculate hash sum
            self.file.seek(0)            
            while True:
                data=self.file.read(8192)
                if not data: break
                m.update(data)
            self.file.seek(0)
            self.hash = m.hexdigest()
    
        return super(PdfDocumentModel, self).save(**kwargs)

    def cacheID(self):
        return self.uuid

    
class DocshotModel(PdfDocumentModel):
    '''
    classdocs
    '''
    tiles_x=models.IntegerField(null=True, blank=True)
    tiles_y=models.IntegerField(null=True, blank=True)
    width=models.IntegerField(null=True, blank=True)
    pagenr=models.IntegerField(null=True, blank=True)
    
    class Meta:
        app_label = 'mediaserver'
    
    def cacheID(self):
        return "docshot_%s_%s_%s_%s_%s" % (super(DocshotModel, self).cacheID(), self.tiles_x, self.tiles_y ,self.width,self.pagenr)  
        
