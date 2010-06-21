# -*- coding: utf-8 -*-

import os
import subprocess

from ecs.mediaserver.storage import Cache


class Renderer(object):
    def render_pages(self, pdf_name, first_page, last_page, zoom, res_x, res_y, pdf_fname):
        args = [ \
            'gs', '-dQUIET', '-dSAFER', '-dBATCH', '-dNOPAUSE', '-sDEVICE=png16m', '-dGraphicsAlphaBits=4', \
            '-dPDFFitPage', '-dTextAlphaBits=4', '-sPAPERSIZE=a4', \
            '-r%.5fx%.5f' % (res_x, res_y), \
            '-dFirstPage=%s' % first_page, '-dLastPage=%s' % last_page, \
            '-sOutputFile=%s_%s_%%04d.png' % (pdf_fname, zoom), \
            pdf_name \
        ]
        print args
        p = subprocess.Popen(args)
        sts = os.waitpid(p.pid, 0)[1]
        print 'sts = %s' % sts


    def render_page(self, png_name_in, png_name, args_compress, args_interlace):
        args = [ 'convert' ] + args_compress + args_interlace + [ png_name_in, png_name ]
        print args
        p = subprocess.Popen(args)
        sts = os.waitpid(p.pid, 0)[1]
        print 'sts = %s' % sts


    def render_bigpage(self, png_names, png_name, zoom, w, h, background, args_compress, args_interlace):
        args = \
            [ 'montage' ] + args_compress + args_interlace + \
            [ '-background', background, '-geometry', '%dx%d+0+0' % (w, h), '-tile', zoom ] + \
            png_names + [ png_name ]
        print args
        p = subprocess.Popen(args)
        sts = os.waitpid(p.pid, 0)[1]
        print 'sts = %s' % sts


    def remove_file(self, file_name):
        print 'removing "%s"' % file_name
        os.remove(file_name)


    def rename_file(self, file_name_old, file_name_new):
        print 'rename "%s" -> "%s"' % (file_name_old, file_name_new)
        os.rename(file_name_old, file_name_new)


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


    def render(self, image_set, single_mode=False, the_page=0, the_zoom=''):
        cm_per_inch = 2.54
        din_a4_x = 21.0
        din_a4_y = 29.7
        background = '#dddddd'
        pdf_name = image_set.set_data.pdf_name
        pages = image_set.set_data.pages
        print 'single_mode: %s' % single_mode
        opt_compress = image_set.set_data.opt_compress
        opt_interlace = image_set.set_data.opt_interlace
        if opt_compress:
            args_compress = [ '-compress', 'Zip', '-quality', '100' ]
        else:
            args_compress = [ ]
        if opt_interlace:
            args_interlace = [ '-interlace', 'PNG' ]
        else:
            args_interlace = [ ]
        print 'opt_compress: %s' % opt_compress
        print 'opt_interlace: %s' % opt_interlace
        errors = 0
        cache = Cache()
        for zoom in image_set.images:
            if single_mode and zoom != the_zoom:
                continue
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
            if zoom == '1':
                if single_mode:
                    page_first = the_page
                    page_last = page_first
                else:
                    page_first = 1
                    page_last = pages
                page_set = range(page_first, page_last + 1)
                self.render_pages(pdf_name, page_first, page_last, '1', res_x, res_y, pdf_fname)
                if single_mode and page_first > 1:
                    name_old = self.get_name(pdf_fname, 1, '1')
                    name_new = self.get_name(pdf_fname, page_first, '1')
                    self.rename_file(name_old, name_new)
                for page in page_set:
                    png_name = self.get_name(pdf_fname, page, '1')
                    if opt_compress or opt_interlace:
                        png_name_in = png_name
                        png_name = self.get_name(pdf_fname, page, '1', False, opt_compress, opt_interlace)
                        self.render_page(png_name_in, png_name, args_compress, args_interlace)
                        self.remove_file(png_name_in)
                    retval = cache.store_page(image_set.id, page, '1', png_name)
                    if not retval:
                        print 'error: cache storage failed'
                        errors += 1
                    else:
                        print 'cache fill: %s' % cache.get_page_key(image_set.id, page, '1')
                    self.remove_file(png_name)
            else:
                bigpages = image_set.render_set.get_bigpages(zoom, pages)
                subpages = subpages_x * subpages_y
                if single_mode:
                    bigpage_first = the_page
                    bigpage_last = bigpage_first
                else:
                    bigpage_first = 1
                    bigpage_last = bigpages
                    self.render_pages(pdf_name, 1, pages, zoom, res_x, res_y, pdf_fname)
                bigpage_set = range(bigpage_first, bigpage_last + 1)
                for bigpage in bigpage_set:
                    page_first = (bigpage - 1) * subpages + 1
                    page_last = min(bigpage * subpages, pages)
                    page_set = range(page_first, page_last + 1)
                    if single_mode:
                        self.render_pages(pdf_name, page_first, page_last, zoom, res_x, res_y, pdf_fname)
                        if page_first > 1:
                            delta = page_last - page_first
                            d_set = range(0, delta + 1)
                            d_set.reverse()
                            for d in d_set:
                                name_old = self.get_name(pdf_fname, 1 + d, zoom)
                                name_new = self.get_name(pdf_fname, page_first + d, zoom)
                                self.rename_file(name_old, name_new)
                    png_names = [ ]
                    for page in page_set:
                        name = self.get_name(pdf_fname, page, zoom)
                        png_names.append(name)
                    png_name = self.get_name(pdf_fname, bigpage, zoom, True, opt_compress, opt_interlace)
                    self.render_bigpage(png_names, png_name, zoom, w, h, background, args_compress, args_interlace)
                    for name in png_names:
                        self.remove_file(name)
                    retval = cache.store_page(image_set.id, bigpage, zoom, png_name)
                    if not retval:
                        print 'error: cache storage failed'
                        errors += 1
                    else:
                        print 'cache fill: %s' % cache.get_page_key(image_set.id, bigpage, zoom)
                    self.remove_file(png_name)
        if errors > 0:
            print '%d error(s)' % errors
            return False
        else:
            return True
