# -*- coding: utf-8 -*-

from ecs.mediaserver.renderset import RenderSet
from ecs.mediaserver.storage import SetData, Storage


class ImageSet(object):

    def __init__(self, id, pages=0):
        self.id = id
        
        self.render_set = RenderSet(1)  # TODO move to storage
        
        storage = Storage()
        # TODO nove out of constructor!
        if pages > 0:
            self.pages = pages
            set_data = SetData(self.pages)
            retval = storage.store_set(self.pages, id)
            if not retval:
                print 'error: can not store set "%s"' % id
                return
        else:
            set_data = storage.load_set(id)
            if set_data is None:
                print 'error: can not load set "%s"' % id
                return
            self.pages = set_data.pages

        # TODO replace with pages_list, e.g. (14,2,1)
        self.images = { }
        for zoom in self.render_set.zoom_list:
            bigpages = self.render_set.get_bigpages(zoom, self.pages)
            page_set = range(1, bigpages + 1)
            self.images[zoom] = dict([(p, { 'url': '/mediaserver/%s/%s/%s/' % (id, p, zoom)}) for p in page_set])
