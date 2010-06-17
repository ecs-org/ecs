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
            '-sOutputFile=%s_%s_%%04d.png ' % (pdf_fname, zoom) + \
            pdf_name
        print cmd
        os.system(cmd)


    def render_page(self, png_name_in, png_name, cmd_compress, cmd_interlace):
        cmd = 'convert %s%s%s %s' % (cmd_compress, cmd_interlace, png_name_in, png_name)
        print cmd
        os.system(cmd)


    def render_bigpage(self, png_names, png_name, zoom, w, h, background, cmd_compress, cmd_interlace):
        cmd = \
            'montage %s%s' % (cmd_compress, cmd_interlace) + \
            '-background \%s ' % background  + \
            '-geometry %dx%d+0+0 ' % (w, h) + \
            '-tile %s ' % zoom + \
            '%s%s' % (png_names, png_name)
        print cmd
        os.system(cmd)


    def remove_file(self, file_name):
        print 'removing "%s"' % file_name
        os.remove(file_name)


    def get_name(self, pdf_fname, page, zoom, is_bigpage=False, opt_compress=False, opt_interlace=False):
        if is_bigpage:
            big = '_big'
        else:
            big = ''
        suffix = ''
        if opt_interlace:
            suffix += '_a7'
        if opt_compress:
            suffix += '_z'
        return '%s_%s%s_%04d%s.png' % (pdf_fname, zoom, big, page, suffix)


    def render(self, image_set):
        cm_per_inch = 2.54
        din_a4_x = 21.0
        din_a4_y = 29.7
        background = '#dddddd'
        pdf_name = image_set.set_data.pdf_name
        pages = image_set.set_data.pages
        opt_compress = image_set.set_data.opt_compress
        opt_interlace = image_set.set_data.opt_interlace
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
        errors = 0
        storage = Storage()
        for zoom in image_set.images:
            print '%s: ' % zoom,
            width = image_set.render_set.width
            height = image_set.render_set.height
            subpages_x = image_set.render_set.get_subpages_x(zoom, pages)
            subpages_y = image_set.render_set.get_subpages_y(zoom, pages)
            w = width / subpages_x
            h = height / subpages_y
            res_x = w / (din_a4_x / cm_per_inch)
            res_y = h / (din_a4_y / cm_per_inch)
            pdf_fname, _ = os.path.splitext(os.path.basename(pdf_name))
            self.render_pages(pdf_name, pages, zoom, res_x, res_y, pdf_fname)
            if zoom == '1':
                for page in image_set.images[zoom]:
                    png_name = self.get_name(pdf_fname, page, zoom)
                    if opt_compress or opt_interlace:
                        png_name_in = png_name
                        png_name = self.get_name(pdf_fname, page, zoom, False, opt_compress, opt_interlace)
                        self.render_page(png_name_in, png_name, cmd_compress, cmd_interlace)
                        self.remove_file(png_name_in)
                    retval = storage.store_page(image_set.id, page, zoom, png_name)
                    if not retval:
                        print 'error: storage failed'
                        errors += 1
                    else:
                        self.remove_file(png_name)
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
                    png_names = ''
                    for page in page_set:
                        png_names += self.get_name(pdf_fname, page, zoom) + ' '
                    png_name = self.get_name(pdf_fname, bigpage, zoom, True, opt_compress, opt_interlace)
                    self.render_bigpage(png_names, png_name, zoom, w, h, background, cmd_compress, cmd_interlace)
                    for page in page_set:
                        name = self.get_name(pdf_fname, page, zoom)
                        self.remove_file(name)
                    retval = storage.store_page(image_set.id, bigpage, zoom, png_name)
                    if not retval:
                        print 'error: storage failed'
                        errors += 1
                    else:
                        self.remove_file(png_name)
        if errors > 0:
            print '%d error(s)' % errors
            return False
        else:
            return True


    def rerender_bigpage(self, id, bigpage, zoom):
        # id -> pdf_name, imageset, opt_compress, opt_interlace
        return
        
