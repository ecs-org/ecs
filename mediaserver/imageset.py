from ecs.mediaserver.renderset import RenderSet


class ImageSet(object):

    def __init__(self, id, pages=0):
        if id == 0:
            self.render_set = RenderSet(1)
            self.pages = pages
        elif id == 1:
            self.render_set = RenderSet(1)
            self.pages = 18
        elif id == 2:
            self.render_set = RenderSet(1)
            self.pages = 14
        else:
            self.render_set = RenderSet(2)
            self.pages = 14

        self.images = { }
        for zoom in self.render_set.zoom_list:
            bigpages = self.render_set.get_bigpages(zoom, self.pages)
            page_set = range(1, bigpages + 1)
            self.images[zoom] = dict([(p, { 'url': '/mediaserver/%s/%s/%s' % (id, p, zoom)}) for p in page_set])
