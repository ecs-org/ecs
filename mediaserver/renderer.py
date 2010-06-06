# -*- coding: utf-8 -*-

import os

from ecs.mediaserver.storage import Storage


class Renderer(object):
    def render_pages(self, pdf_name, pages, zoom, res_x, res_y, pdf_fname):
        cmd = \
            'gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 ' + \
            '-dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 ' + \
            '-r%.5fx%.5f ' % (res_x, res_y) + \
            '-dFirstPage=1 -dLastPage=%s ' % pages + \
            '-sOutputFile=%s_%s_%%04d_ni.png ' % (pdf_fname, zoom) + \
            pdf_name
        print cmd
        os.system(cmd)

    def render_interlaced(self, png_ni_name, png_name, cmd_compress, cmd_interlace):
        cmd = 'convert %s%s%s %s' % (cmd_compress, cmd_interlace, png_ni_name, png_name)
        print cmd
        os.system(cmd)

    def render_bigpage(self, png_ni_names, png_name, zoom, w, h, background, cmd_compress, cmd_interlace):
        cmd = \
            'montage %s%s' % (cmd_compress, cmd_interlace) + \
            '-background \%s ' % background  + \
            '-geometry %dx%d+0+0 ' % (w, h) + \
            '-tile %s ' % zoom + \
            '%s%s' % (png_ni_names, png_name)
        print cmd
        os.system(cmd)

    def remove_file(self, file_name):
        print 'removing "%s"' % file_name
        os.remove(file_name)

    def render(self, pdf_name, image_set, opt_compress, opt_interlace):
        cm_per_inch = 2.54
        din_a4_x = 21.0
        din_a4_y = 29.7
        background = '#dddddd'
        if opt_compress:
            cmd_compress = '-compress Zip -quality 100 '  # keep blank at end
        else:
            cmd_compress = ''
        if opt_interlace:
            cmd_interlace = '-interlace PNG '  # keep blank at end
        else:
            cmd_interlace = ''
        print 'opt_compress: %s' % opt_compress
        print 'opt_interlace: %s' % opt_interlace
        storage = Storage()
        pages = image_set.pages
        for zoom in image_set.images:
            print '%s: ' % zoom,
            width = image_set.render_set.width
            height = image_set.render_set.height
            subpages_x = image_set.render_set.get_subpages_x(zoom, pages)
            subpages_y = image_set.render_set.get_subpages_y(zoom, pages)
            res_x = (width / (din_a4_x / cm_per_inch)) / subpages_x
            res_y = (height / (din_a4_y / cm_per_inch)) / subpages_y
            pdf_fname, _ = os.path.splitext(os.path.basename(pdf_name))
            self.render_pages(pdf_name, pages, zoom, res_x, res_y, pdf_fname)
            if zoom == '1':
                for page in image_set.images[zoom]:
                    png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                    if opt_interlace:
                        png_name = '%s_%s_%04d.png' % (pdf_fname, zoom, page)
                        self.render_interlaced(png_ni_name, png_name, cmd_compress, cmd_interlace)
                        self.remove_file(png_ni_name)
                        image_name = png_name
                    else:
                        image_name = png_ni_name
                    rc = storage.store_page(image_name, image_set.id, page, zoom)                  
                    if not rc:
                        print 'error: storage failed'
                        return False
            else:
                bigpages = image_set.render_set.get_bigpages(zoom, pages)
                bigpage_set = range(1, bigpages + 1)
                subpages = image_set.render_set.get_subpages(zoom, pages)
                w = width / subpages_x
                h = height / subpages_y
                for bigpage in bigpage_set:
                    page_first = (bigpage - 1) * subpages + 1
                    page_last = min(bigpage * subpages, pages)
                    page_set = range(page_first, page_last + 1)
                    png_ni_names = ''
                    for page in page_set:
                        png_ni_names += '%s_%s_%04d_ni.png ' % (pdf_fname, zoom, page)
                    if opt_interlace:
                        png_name = '%s_%s_big_%04d.png' % (pdf_fname, zoom, bigpage)
                    else:
                        png_name = '%s_%s_big_%04d_ni.png' % (pdf_fname, zoom, bigpage)
                    self.render_bigpage(png_ni_names, png_name, zoom, w, h, background, cmd_compress, cmd_interlace)
                    for page in page_set:
                        png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                        self.remove_file(png_ni_name)
                    rc = storage.store_page(png_name, image_set.id, bigpage, zoom)
                    if not rc:
                        print 'error: storage failed'
        return True
