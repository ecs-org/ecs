# -*- coding: utf-8 -*-
import hashlib
import os
import posixpath
import tempfile
import datetime
import mimetypes
from uuid import uuid4

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.utils._os import safe_join
from django.utils.encoding import smart_str
from django.conf import settings
from django.core.exceptions import ValidationError

from ecs.utils.pdfutils import pdf_barcodestamp, pdf_pages, pdf_isvalid


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=30, db_index=True, blank=True, default= "")
    helptext = models.TextField(blank=True, default="")

    def __unicode__(self):
        return self.name

def storing_document_to(instance=None, filename=None):
    # the file path is derived from the document uuid. This should be
    # random enough, so we do not have collisions in the next gogolplex years
    dirs = list(instance.uuid_document[:6]) + [instance.uuid_document]
    return os.path.join(settings.FILESTORE, *dirs)

def incoming_document_to(instance=None, filename=None):
    instance.original_file_name = os.path.basename(os.path.normpath(filename)) # save original_file_name
    target_name = os.path.normpath(os.path.join(settings.FILESTORE, 'incoming', instance.uuid_document, instance.original_file_name))
    #print("incoming document to: original file name %s , target_name %s " % (instance.original_file_name, target_name))
    return target_name
    
class DocumentFileStorage(FileSystemStorage):

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        Limit the length to some reasonable value.
        """

        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add _ with a 4 digit number till we get an empty slot.
        counter = 0
        while self.exists(name):
            # file_ext includes the dot.
            counter += 1
            name = os.path.join(dir_name, "%s_%04d%s" % (file_root, counter, file_ext))
        return name

    def path(self, name):
        # We need to overwrite the default behavior, because django won't let us save documents outside of MEDIA_ROOT
        return smart_str(os.path.normpath(name))


class DocumentManager(models.Manager):
    def create_from_buffer(self, buf, **kwargs):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(buf)
        tmp.flush()
        tmp.seek(0)
        kwargs.setdefault('date', datetime.datetime.now())
        doc = self.create(file=File(tmp), **kwargs)
        tmp.close()
        return doc

class Document(models.Model):
    uuid_document = models.SlugField(max_length=36)
    hash = models.SlugField(max_length=32)
    file = models.FileField(null=True, upload_to=incoming_document_to, storage=DocumentFileStorage())
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    doctype = models.ForeignKey(DocumentType, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    pages = models.IntegerField(null=True, blank=True)

    version = models.CharField(max_length=250)
    date = models.DateTimeField()
    deleted = models.BooleanField(default=False, blank=True)
    
    objects = DocumentManager()
    
    def __unicode__(self):
        t = "Sonstige Unterlagen"
        if self.doctype_id:
            t = self.doctype.name
        return "%s Version %s vom %s" % (t, self.version, self.date.strftime('%d.%m.%Y'))

    def copy_to(self, upload_to):
        ''' temporary helper, takes path returned from function upload_to(object, originalfilename), and copies it there '''
        dir=os.path.abspath(upload_to(self,self.file.name))
        if not os.path.exists(dir):
            os.makedirs(dir)
        tmp = tempfile.NamedTemporaryFile(delete=False, dir=dir, suffix=os.path.splitext(self.file.name)[1])
        filename = tmp.name
        print("copying to %s" % filename)
        buf = ''
        self.file.seek(0)
        while True:
            buf = self.file.read(8192)
            if not buf: break
            tmp.write(buf)
        tmp.close()
        return filename

    def save(self, **kwargs):
        if not self.file:
            raise ValueError('no file')

        if not self.uuid_document: 
            self.uuid_document = str(uuid4()) # generate a new random uuid
            content_type, encoding = mimetypes.guess_type(self.file.name) # look what kind of mimetype we would guess

            if self.mimetype == 'application/pdf' or content_type == 'application/pdf':
                if not pdf_isvalid(self.file):
                    raise ValidationError('no valid pdf')			
      
            if self.mimetype == 'application/pdf' or content_type == 'application/pdf':
                if getattr(settings, 'ECS_AUTO_PDF_BARCODE', True): 
                    # FIXME: call stampbarcode only if we have pdftk on the platform (currently no mac)
                    # FIXME: we dont call stampbarcode anymore, because barcode stamping will be done later, just before downloading, which is not happening but thats the idea ;-)
                    """
                    newfile = File(tempfile.NamedTemporaryFile(dir=os.path.join(settings.FILESTORE)))
                    pdf_barcodestamp(self.file, newfile, self.uuid_document)
                    self.file.close()
                    self.file = newfile
                    """
                    
        if not self.hash:
            m = hashlib.md5() # calculate hash sum
            self.file.seek(0)            
            while True:
                data= self.file.read(8192)
                if not data: break
                m.update(data)
            self.file.seek(0)
            self.hash = m.hexdigest()

        if self.mimetype == 'application/pdf':
            self.pages = pdf_pages(self.file) # calculate number of pages

        return super(Document, self).save(**kwargs)
  
class Page(models.Model):
    doc = models.ForeignKey(Document)
    num = models.PositiveIntegerField()
    text = models.TextField()


def _post_doc_save(sender, **kwargs):
    from ecs.documents.task_queue import extract_and_index_pdf_text
    from ecs.mediaserver.task_queue import cache_and_render
    doc = kwargs['instance']
    doc.page_set.all().delete()
    print("doc file %s , path %s, original %s" % (str(doc.file.name), str(doc.file.path), str(doc.original_file_name)))
    if doc.pages and doc.mimetype == 'application/pdf':
        # FIXME: we use a 3 seconds wait to prevent celery from picking up the tasks before the current transaction is committed.
        extract_and_index_pdf_text.apply_async(args=[doc.pk], countdown=3)
        cache_and_render.apply_async(args=[doc.pk], countdown=3)

def _post_page_delete(sender, **kwargs):
    from haystack import site
    site.get_index(Page).remove_object(kwargs['instance'])

post_save.connect(_post_doc_save, sender=Document)
post_delete.connect(_post_page_delete, sender=Page)
