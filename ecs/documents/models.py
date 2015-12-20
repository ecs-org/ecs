# -*- coding: utf-8 -*-
import tempfile
import mimetypes
import logging
import uuid

from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.utils.translation import ugettext
from django.utils import timezone

from ecs.authorization import AuthorizationManager
from ecs.utils.pdfutils import pdf_barcodestamp
from ecs.documents.storagevault import getVault


logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=30, db_index=True, blank=True, default= "")
    helptext = models.TextField(blank=True, default="")
    is_hidden = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    def __unicode__(self):
        return ugettext(self.name)


class DocumentManager(AuthorizationManager): 
    def create_from_buffer(self, buf, **kwargs): 
        if 'doctype' in kwargs and isinstance(kwargs['doctype'], basestring):
            kwargs['doctype'] = DocumentType.objects.get(identifier=kwargs['doctype'])

        now = timezone.now()
        kwargs.setdefault('date', now)
        kwargs.setdefault('version', str(now))

        doc = self.create(**kwargs)
        with tempfile.TemporaryFile() as f:
            f.write(buf)
            f.flush()
            f.seek(0)
            doc.store(f)
        return doc


class Document(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    original_file_name = models.CharField(max_length=250, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    stamp_on_download = models.BooleanField(default=True)

    # user supplied data
    name = models.CharField(max_length=250)
    doctype = models.ForeignKey(DocumentType)
    version = models.CharField(max_length=250)
    date = models.DateTimeField()
    replaces_document = models.ForeignKey('Document', null=True, blank=True)
    
    # relation to a object
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_object = GenericForeignKey('content_type', 'object_id')
    
    objects = DocumentManager()
    
    def __unicode__(self):
        t = "Sonstige Unterlagen"
        if self.doctype_id:
            t = self.doctype.name
        return u'{0} {1}-{2} vom {3}'.format(t, self.name, self.version, self.date.strftime('%d.%m.%Y'))

    def get_filename(self):
        if self.mimetype == 'application/vnd.ms-excel': # HACK: we want .xls not .xlb for excel files
            ext = '.xls'
        else:
            ext = mimetypes.guess_extension(self.mimetype) or '.bin'
        name_slices = [self.doctype.name if self.doctype else 'Unterlage', self.name, self.version, self.date.strftime('%Y.%m.%d')]
        if self.parent_object and hasattr(self.parent_object, 'get_filename_slice'):
            name_slices.insert(0, self.parent_object.get_filename_slice())
        name = slugify('-'.join(name_slices))
        return ''.join([name, ext])

    def store(self, f):
        getVault()[self.uuid.get_hex()] = f

    def retrieve(self, user, context):
        hist = DownloadHistory.objects.create(document=self, user=user,
            context=context)

        f = getVault()[self.uuid.get_hex()]
        if self.mimetype == 'application/pdf' and self.stamp_on_download:
            f = pdf_barcodestamp(f, hist.uuid.get_hex(), unicode(user))
        return f


class DownloadHistory(models.Model):
    document = models.ForeignKey(Document, db_index=True)
    user = models.ForeignKey(User)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    context = models.CharField(max_length=15)

    class Meta:
        ordering = ['downloaded_at']
