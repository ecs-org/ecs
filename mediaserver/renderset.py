class RenderSet(object):
    def __init__(self, id):
        if id == 1:
            self.zoom_list = [ '1', '3x3', '5x5' ]
            self.zoom_pages = [ [1,1], [3,3], [5,5] ]
            self.width = 800
            self.height = 1131
        else:
            self.zoom_list = [ '1', '6x3', '10x5' ]
            self.zoom_pages = [ [1,1], [6,3], [10,5] ]
            self.width = 800
            self.height = 1131
        self.zooms = len(self.zoom_list)

    def get_subpages_x(self, zoom, pages):
        zoom_index = self.zoom_list.index(zoom)
        subpages_x = self.zoom_pages[zoom_index][0]
        return subpages_x

    def get_subpages_y(self, zoom, pages):
        zoom_index = self.zoom_list.index(zoom)
        subpages_y = self.zoom_pages[zoom_index][1]
        return subpages_y

    def get_subpages(self, zoom, pages):
        subpages_x = self.get_subpages_x(zoom, pages)
        subpages_y = self.get_subpages_y(zoom, pages)
        subpages = subpages_x * subpages_y
        return subpages

    def get_bigpages(self, zoom, pages):
        subpages = self.get_subpages(zoom, pages)
        bigpages = (pages - 1) / subpages + 1
        return bigpages

    def has_zoom(self, zoom):
        return self.zoom_list.count(zoom) > 0
