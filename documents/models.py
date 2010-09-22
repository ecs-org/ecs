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
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from ecs.utils.pdfutils import pdf_barcodestamp, pdf_pages, pdf_isvalid
from ecs import authorization


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=30, db_index=True, blank=True, default= "")
    helptext = models.TextField(blank=True, default="")

    def __unicode__(self):
        return self.name


def incoming_document_to(instance=None, filename=None):
    instance.original_file_name = os.path.basename(os.path.normpath(filename)) # save original_file_name
    target_name = os.path.normpath(os.path.join(settings.INCOMING_FILESTORE, instance.uuid_document, instance.original_file_name))
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


class DocumentManager(authorization.AuthorizationManager): 
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
    
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_object = GenericForeignKey('content_type', 'object_id')
    
    objects = DocumentManager()
    
    def __unicode__(self):
        t = "Sonstige Unterlagen"
        if self.doctype_id:
            t = self.doctype.name
        return "%s Version %s vom %s" % (t, self.version, self.date.strftime('%d.%m.%Y'))

    def save(self, **kwargs):
        if not self.file:
            raise ValueError('no file')

        if not self.uuid_document: 
            self.uuid_document = uuid4().get_hex() # generate a new random uuid
            content_type, encoding = mimetypes.guess_type(self.file.name) # look what kind of mimetype we would guess

            if self.mimetype == 'application/pdf' or content_type == 'application/pdf':
                if not pdf_isvalid(self.file):
                    raise ValidationError('no valid pdf')

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


class DocumentAuthorizationQFactory(authorization.AuthorizationQFactory):
    def get_q(self, user):
        from ecs.core.models import SubmissionForm
        submission_q = models.Q(content_type=ContentType.objects.get_for_model(SubmissionForm))
        q = ~submission_q | (submission_q & models.Q(object_id__in=SubmissionForm.objects.values('pk').query))
        return q

authorization.register(Document, DocumentAuthorizationQFactory)

class Page(models.Model):
    doc = models.ForeignKey(Document)
    num = models.PositiveIntegerField()
    text = models.TextField()


def _post_doc_save(sender, **kwargs):
    from ecs.documents.task_queue import extract_and_index_pdf_text
    from ecs.documents.task_queue import encrypt_and_upload_to_storagevault
    
    doc = kwargs['instance']
    doc.page_set.all().delete()
    
    print("doc file %s , path %s, original %s" % (str(doc.file.name), str(doc.file.path), str(doc.original_file_name)))
    
    if doc.pages and doc.mimetype == 'application/pdf':
        # FIXME: we use a 3 seconds wait to prevent celery from picking up the tasks before the current transaction is committed.
        extract_and_index_pdf_text.apply_async(args=[doc.pk], countdown=3)
    
    # upload it via celery to the storage vault
    encrypt_and_upload_to_storagevault.apply_async(args=[doc.pk], countdown=3)
        
        
def _post_page_delete(sender, **kwargs):
    from haystack import site
    site.get_index(Page).remove_object(kwargs['instance'])

post_save.connect(_post_doc_save, sender=Document)
post_delete.connect(_post_page_delete, sender=Page)


