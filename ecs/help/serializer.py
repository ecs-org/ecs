import json
import zipfile

from ecs.help.models import Page, Attachment
from ecs.tracking.models import View

from reversion import revisions as reversion

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
            try:
                func = getattr(self, 'load_{0}'.format(f))
            except AttributeError:
                kwargs[f] = data[f]
            else:
                kwargs[f] = func(zf, data, extra=extra)

        create_kwargs = dict((k, kwargs.pop(k)) for k in self.unique)
        create_kwargs['defaults'] = kwargs
        instance, created = self.model.objects.get_or_create(**create_kwargs)
        for k, v in kwargs.items():
            setattr(instance, k, v)
        with reversion.create_revision():
            instance.save()
        return instance

class PageSerializer(Serializer):
    fields = ['view', 'anchor', 'slug', 'title', 'text', 'review_status']
    unique = ['slug']
    model = Page

    def serialize_view(self, zf, instance):
        return instance.view.path if instance.view else None

    def load_view(self, zf, data, extra=None):
        return View.objects.get_or_create(path=data['view'])[0] if data['view'] else None

class AttachmentSerializer(Serializer):
    fields = ['content', 'mimetype', 'is_screenshot', 'slug', 'view', 'page']
    unique = ['slug']
    model = Attachment

    def serialize_content(self, zf, instance):
        zip_name = 'attachments/{0}'.format(instance.slug)
        zf.writestr(zip_name, instance.content)
        return zip_name

    def serialize_view(self, zf, instance):
        return instance.view.path if instance.view else None

    def serialize_page(self, zf, instance):
        return str(instance.page.pk) if instance.page else None

    def load_content(self, zf, data, extra=None):
        if 'file' in data:      # compat
            fname = data['file']
        else:
            fname = data['content']
        return zf.read(fname)

    def load_view(self, zf, data, extra=None):
        return View.objects.get_or_create(path=data['view'])[0] if data['view'] else None

    def load_page(self, zf, data, extra):
        page_pks = extra
        old_pk = data['page']
        if not old_pk:
            return None
        old_pk = str(old_pk)
        new_pk = int(page_pks[old_pk])
        return Page.objects.get(pk=new_pk)

    def load_is_screenshot(self, zf, data, extra=None):
        ''' XXX: quirks for renamed model field '''
        try:
            return data['is_screenshot']
        except KeyError:
            return data['screenshot']

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
    
    zf.writestr('data.json', json.dumps(data))

def load(file_like):
    zf = zipfile.ZipFile(file_like, 'r')
    data = json.loads(zf.read('data.json').decode('utf-8'))

    page_pks = {}
    page_serializer = PageSerializer()
    for old_pk, d in data['pages'].items():
        page = page_serializer.load(zf, d)
        page_pks[old_pk] = page.pk

    attachment_serializer = AttachmentSerializer()
    for a in data['attachments']:
        attachment = attachment_serializer.load(zf, a, extra=page_pks)


