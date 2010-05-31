from ecs.mediaserver.renderset import RenderSet


class ImageSet(object):
    def __init__(self, id):
        if id == 1:
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
            page_set = range(1, self.render_set.get_bigpages(zoom, self.pages) + 1)
            self.images[zoom] = dict([(page, { 'url': '/mediaserver/%s/%s/%s' % (id, page, zoom)}) for page in page_set])
