# -*- coding: utf-8 -*-

import hashlib
import os
import tempfile
from uuid import uuid4

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str
from django.conf import settings
from django.core.exceptions import ValidationError

from ecs.utils.pdfutils import stamp_pdf
from ecs.mediaserver.analyzer import Analyzer


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return self.name

def upload_document_to(instance=None, filename=None):
    # the file path is derived from the document uuid. This should be
    # random enough, so we do not have collisions in the next gogolplex years
    dirs = list(instance.uuid_document[:6]) + [instance.uuid_document]
    return os.path.join(settings.FILESTORE, *dirs)


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


class Document(models.Model):
    uuid_document = models.SlugField(max_length=36)
    hash = models.SlugField(max_length=32)
    file = models.FileField(null=True, upload_to=upload_document_to, storage=DocumentFileStorage())
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    doctype = models.ForeignKey(DocumentType, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    pages = models.IntegerField(null=True, blank=True)

    version = models.CharField(max_length=250)
    date = models.DateTimeField()
    deleted = models.BooleanField(default=False, blank=True)
    
    class Meta:
        app_label = 'core'
        
    def __unicode__(self):
        t = "Sonstige Unterlagen"
        if self.doctype_id:
            t = self.doctype.name
        return "%s Version %s vom %s" % (t, self.version, self.date.strftime('%d.%m.%Y'))

    def save(self, **kwargs):
        """ TODO: handel other filetypes than PDFs """
        if self.file:
            if not self.uuid_document and getattr(settings, 'ECS_AUTO_PDF_BARCODE', True): # if uuid is given, dont stamp the pdf
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                filename = tmp.name
                buf = ''
                while True:
                    buf = self.file.read(4096)
                    if not buf: break
                    tmp.write(buf)
                tmp.close()
                self.file.close()
                
                self.uuid_document = str(uuid4())
                self.file = stamp_pdf(filename, self.uuid_document)
                    
                os.remove(filename)
            
            m = hashlib.md5()        # update hash sum
            while True:
                buf = self.file.read(4096)
                if not buf: break
                m.update(buf)
            self.file.seek(0)
            self.hash = m.hexdigest()
            
            analyzer = Analyzer()     # update page number
            analyzer.sniff_file(self.file)
            if analyzer.valid is False:
                raise ValidationError('invalid PDF')  # TODO add user-visible error message
            self.pages = analyzer.pages
        
        return super(Document, self).save(**kwargs)
        
class Page(models.Model):
    doc = models.ForeignKey(Document)
    num = models.PositiveIntegerField()
    text = models.TextField()
    
    class Meta:
        app_label = 'core'

def _post_doc_save(sender, **kwargs):
    from ecs.core.task_queue import extract_and_index_pdf_text
    from ecs.mediaserver.task_queue import cache_and_render
    doc = kwargs['instance']
    doc.page_set.all().delete()
    if doc.pages and doc.mimetype == 'application/pdf':
        extract_and_index_pdf_text.apply_async(args=[doc.pk], countdown=3)
        cache_and_render.apply_async(args=[doc.pk], countdown=3)

def _post_page_delete(sender, **kwargs):
    from haystack import site
    site.get_index(Page).remove_object(kwargs['instance'])

post_save.connect(_post_doc_save, sender=Document)
post_delete.connect(_post_page_delete, sender=Page)
