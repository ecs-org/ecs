# -*- coding: utf-8 -*-

from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.renderset import RenderSet
from ecs.mediaserver.storage import SetData, Storage


class ImageSet(object):

    def __init__(self, id, pages=0):
        self.id = id
        self.render_set = RenderSet(1)
        self.images = None
        self.set_data = None


    def init_images(self):
        # image data to be delivered as JSON for the PDF viewer:
        #   { <zoom>: { <page>: { 'url': <url>, .. } } }
        self.images = { }
        for zoom in self.render_set.zoom_list:
            bigpages = self.render_set.get_bigpages(zoom, self.set_data.pages)
            page_set = range(1, bigpages + 1)
            self.images[zoom] = dict([(p, { 'url': '/mediaserver/%s/%s/%s/' % (self.id, p, zoom)}) for p in page_set])


    def store(self, origin, pdf_name, pages, opt_compress=True, opt_interlace=True):
        storage = Storage()
        self.set_data = SetData(origin, pdf_name, pages, opt_compress, opt_interlace)
        retval = storage.store_set(self.id, self.set_data)
        if not retval:
            return False
        self.init_images()
        return True


    def load(self):
        storage = Storage()
        set_data = storage.load_set(self.id)
        if set_data is None:
            # TODO id could be invalid or item was squeezed out of the cache by its replacement strategy,
            # so we need to query the database for the needed data here
            return False
        self.set_data = set_data
        self.init_images()
        return True


    def store_document(self, document):
        if self.store('Document', document.file.name, document.pages) is False:
            print 'store_document: can not store ImageSet "%s"' % document.id
            return
        renderer = Renderer()
        renderer.render(self)
