import zipfile
import tempfile
from uuid import uuid4

from django.utils import simplejson
from django.core.files.base import ContentFile

from ecs.help.models import Page, Attachment
from ecs.tracking.models import View


class Serializer(object):
    fields = []
    unique = []
    model = None

    def serialize(self, zf, instance):
        data = {}
        for f in self.fields:
            v = getattr(instance, f)
            try:
                func = getattr(self, 'serialize_{0}'.format(f))
            except AttributeError:
                data[f] = v
            else:
                data[f] = func(zf, instance)

        return data

    def load(self, zf, data, extra=None):
        kwargs = {}
        for f in self.fields:
            v = data[f]
            try:
                func = getattr(self, 'load_{0}'.format(f))
            except AttributeError:
                kwargs[f] = v
            else:
                kwargs[f] = func(zf, data, extra=extra)

        unique = dict((k, kwargs.pop(k)) for k in self.unique)
        instance, created = self.model.objects.get_or_create(**unique)
        for k, v in kwargs.iteritems():
            setattr(instance, k, v)
        instance.save()
        return instance

class PageSerializer(Serializer):
    fields = ['view', 'anchor', 'slug', 'title', 'text']
    unique = ['view', 'anchor']
    model = Page

    def serialize_view(self, zf, instance):
        return instance.view.path if instance.view else None

    def load_view(self, zf, data, extra=None):
        return View.objects.get(path=data['view']) if data['view'] else None

class AttachmentSerializer(Serializer):
    fields = ['file', 'mimetype', 'screenshot', 'slug', 'view', 'page']
    unique = ['slug']
    model = Attachment

    def serialize_file(self, zf, instance):
        zip_name = 'attachments/{0}'.format(instance.slug)
        zf.writestr(zip_name, instance.file.read())
        return zip_name

    def serialize_view(self, zf, instance):
        return instance.view.path if instance.view else None

    def serialize_page(self, zf, instance):
        return str(instance.page.pk) if instance.page else None

    def load_file(self, zf, data, extra=None):
        fname = data['file']
        f = ContentFile(zf.read(fname))
        f.name = fname
        return f

    def load_view(self, zf, data, extra=None):
        return View.objects.get(path=data['view']) if data['view'] else None

    def load_page(self, zf, data, extra):
        page_pks = extra
        old_pk = str(data['page'])
        if not old_pk:
            return None
        new_pk = int(page_pks[old_pk])
        return Page.objects.get(pk=new_pk)

def export(file_like):
    zf = zipfile.ZipFile(file_like, 'w', zipfile.ZIP_DEFLATED)
    data = {}

    data['attachments'] = []
    attachment_serializer = AttachmentSerializer()
    for a in Attachment.objects.all():
        data['attachments'].append(attachment_serializer.serialize(zf, a))

    data['pages'] = {}
    page_serializer = PageSerializer()
    for p in Page.objects.all():
        data['pages'][str(p.pk)] = page_serializer.serialize(zf, p)

    zf.writestr('data.json', simplejson.dumps(data))

def load(file_like):
    zf = zipfile.ZipFile(file_like, 'r')
    data = simplejson.loads(zf.read('data.json'))

    page_pks = {}
    page_serializer = PageSerializer()
    for old_pk, d in data['pages'].iteritems():
        page = page_serializer.load(zf, d)
        page_pks[old_pk] = page.pk

    attachment_serializer = AttachmentSerializer()
    for a in data['attachments']:
        attachment = attachment_serializer.load(zf, a, extra=page_pks)


