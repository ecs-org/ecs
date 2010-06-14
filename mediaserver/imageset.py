# -*- coding: utf-8 -*-

from ecs.mediaserver.renderset import RenderSet
from ecs.mediaserver.storage import SetData, Storage


class ImageSet(object):

    def __init__(self, id, pages=0):
        self.id = id
        self.render_set = RenderSet(1)
        self.pages = 0


    def init_images(self):
        self.images = { }
        for zoom in self.render_set.zoom_list:
            bigpages = self.render_set.get_bigpages(zoom, self.pages)
            page_set = range(1, bigpages + 1)
            self.images[zoom] = dict([(p, { 'url': '/mediaserver/%s/%s/%s/' % (self.id, p, zoom)}) for p in page_set])


    def store(self, pages):
        storage = Storage()
        self.pages = pages
        set_data = SetData(self.pages)
        retval = storage.store_set(self.pages, self.id)
        if not retval:
            return False
        self.init_images()
        return True


    def load(self):
        storage = Storage()
        set_data = storage.load_set(self.id)
        if set_data is None:
            return False
        self.pages = set_data.pages
        self.init_images()
        return True
