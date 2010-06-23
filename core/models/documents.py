# -*- coding: utf-8 -*-

import hashlib
import os
import tempfile
from uuid import uuid4

from django.db import models
from django.db.models.signals import post_save
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File

from ecs.utils.pdfutils import stamp_pdf
from ecs.mediaserver.analyzer import Analyzer
from ecs.mediaserver.signals import document_post_save


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

    def save(self, **kwargs):
        if self.file:
            m = hashlib.md5()

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            filename = tmp.name
            buf = ''
            while True:
                buf = self.file.read(4096)  # we iterate over the file, so we
                if not buf: break  # do not have to hold the whole thingy in
                                    # ram
                m.update(buf)
                tmp.write(buf)
            tmp.close()
            self.file.seek(0)
            
            self.hash = m.hexdigest()
            self.uuid_document = str(uuid4())
            
            nu_file = stamp_pdf(filename, self.uuid_document)
            os.remove(filename)

            self.file.close()
            self.file = File(nu_file)
            
            analyzer = Analyzer()
            analyzer.sniff_file(self.file)
            if analyzer.valid is False:
                raise ValidationError('invalid PDF')  # TODO add user-visible error message
            self.pages = analyzer.pages
            
            return super(Document, self).save(**kwargs)


post_save.connect(document_post_save, sender=Document)


