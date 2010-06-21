# -*- coding: utf-8 -*-

from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.renderset import RenderSet
from ecs.mediaserver.storage import Cache, SetData


class ImageSet(object):

    def __init__(self, id, set_data=None):
        self.id = id
        self.render_set = RenderSet(1)
        self.images = None
        self.set_data = set_data


    def init_images(self):
        # image data to be delivered as JSON for the PDF viewer:
        #   { <zoom>: { <page>: { 'url': <url>, .. } } }
        self.images = { }
        for zoom in self.render_set.zoom_list:
            bigpages = self.render_set.get_bigpages(zoom, self.set_data.pages)
            page_set = range(1, bigpages + 1)
            self.images[zoom] = dict([(p, { 'url': '/mediaserver/%s/%s/%s/' % (self.id, p, zoom)}) for p in page_set])


    def store(self, origin, pdf_name, pages):
        cache = Cache()
        self.set_data = SetData(origin, pdf_name, pages)
        retval = cache.store_set(self.id, self.set_data)
        if not retval:
            print 'cache fill failed: set "%s"' % cache.get_set_key(self.id)
            return False
        self.init_images()
        return True


    def load(self):
        cache = Cache()
        set_data = cache.load_set(self.id)
        if set_data is None:
            print 'cache miss: set "%s"' % cache.get_set_key(self.id)
            return False
        self.set_data = set_data
        self.init_images()
        return True


def cache_and_render(document):
    id = document.pk
    image_set = ImageSet(id)
    if image_set.store('doc save', document.file.name, document.pages) is False:
        print 'cache_and_render: can not store ImageSet "%s"' % document.id
        return False
    renderer = Renderer()
    renderer.render(image_set)
    cache = Cache()
    print 'rendered key "%s", set "%s"' % (cache.get_set_key(image_set.id), image_set.set_data)
