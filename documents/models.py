# -*- coding: utf-8 -*-

import hashlib
import os
import tempfile
import datetime
import mimetypes
import logging
from uuid import uuid4
from contextlib import contextmanager
from shutil import copyfileobj

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.files.base import File
from django.utils.encoding import smart_str
from django.conf import settings
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from ecs.authorization import AuthorizationManager
from ecs.utils.pdfutils import pdf_barcodestamp
from ecs.mediaserver.storagevault import getVault


logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=30, db_index=True, blank=True, default= "")
    helptext = models.TextField(blank=True, default="")
    is_hidden = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    def __unicode__(self):
        return ugettext(self.name)


def incoming_document_to(instance=None, filename=None):
    instance.original_file_name = os.path.basename(os.path.normpath(filename)) # save original_file_name
    _, file_ext = os.path.splitext(filename)
    target_name = os.path.normpath(os.path.join(settings.INCOMING_FILESTORE, instance.uuid + file_ext[:5]))
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


class DocumentManager(AuthorizationManager): 
    def create_from_buffer(self, buf, **kwargs): 
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmpname = tmp.name
        tmp.write(buf)
        tmp.flush()
        tmp.seek(0)

        if 'doctype' in kwargs and isinstance(kwargs['doctype'], basestring):
            kwargs['doctype'] = DocumentType.objects.get(identifier=kwargs['doctype'])

        kwargs.setdefault('date', datetime.datetime.now())
        doc = self.create(file=File(open(tmpname,'rb')), **kwargs)
        tmp.close()
        return doc


C_STATUS_CHOICES = (
    ('new', _('new')),
    ('uploading', _('uploading')),
    ('ready', _('ready')),
    ('aborted', _('aborted')),
    ('deleted', _('deleted')),
)

class Document(models.Model):
    uuid = models.SlugField(max_length=36, unique=True, default=lambda: uuid4().get_hex())
    hash = models.SlugField(max_length=32)
    original_file_name = models.CharField(max_length=250, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    stamp_on_download = models.BooleanField(default=True)
    status = models.CharField(max_length=15, default='new', choices=C_STATUS_CHOICES)
    retries = models.IntegerField(default=0, editable=False)

    # user supplied data
    file = models.FileField(null=True, upload_to=incoming_document_to, storage=DocumentFileStorage(), max_length=250)
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
    
    @property
    def doctype_name(self):
        if self.doctype_id:
            return _(self.doctype.name)
        return u"Sonstige Unterlagen"
    
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

    def get_from_mediaserver(self):
        ''' load actual data from storage vault including optional stamp ; you rarely use this. '''
        f = None
        vault = getVault()

        if self.mimetype == 'application/pdf' and self.stamp_on_download:
            inputpdf = vault.get(self.uuid)
            # XXX: stamp personalized uuid
            f = pdf_barcodestamp(inputpdf, self.uuid)
            vault.decommission(inputpdf)
        else:
            f = vault.get(self.uuid)

        return f
    
    def save(self, **kwargs):
        if not self.hash:
            m = hashlib.md5() # calculate hash sum
            self.file.seek(0)
            while True:
                data= self.file.read(8192)
                if not data: break
                m.update(data)
            self.file.seek(0)
            self.hash = m.hexdigest()

        return super(Document, self).save(**kwargs)


class DownloadHistory(models.Model):
    document = models.ForeignKey(Document, db_index=True)
    user = models.ForeignKey(User)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['downloaded_at']
