# -*- coding: utf-8 -*-

import os

from ecs.mediaserver.storage import Storage


class Renderer(object):
    def render(self, pdf_name, image_set):
        compress = True
        if compress:
            opt_compress = '-compress Zip -quality 100 '
        else:
            opt_compress = ''
        cm_per_inch = 2.54
        din_a4_x = 21.0
        din_a4_y = 29.7
        background = '#dddddd'
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
            gs_cmd = \
                'gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 ' + \
                '-dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 ' + \
                '-r%.5fx%.5f ' % (res_x, res_y) + \
                '-dFirstPage=1 -dLastPage=%s ' % pages + \
                '-sOutputFile=%s_%s_%%04d_ni.png ' % (pdf_fname, zoom) + \
                pdf_name
            print gs_cmd
            os.system(gs_cmd)
            if zoom == '1':
                for page in image_set.images[zoom]:
                    png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                    png_name = '%s_%s_%04d.png' % (pdf_fname, zoom, page)
                    im_cmd = 'convert %s-interlace PNG %s %s' % (opt_compress, png_ni_name, png_name)
                    print im_cmd
                    os.system(im_cmd)
                    rm_cmd = 'rm %s' % png_ni_name
                    print rm_cmd
                    os.system(rm_cmd)
                    storage.store(png_name, page, zoom)  # TODO remove png
            else:
                bigpages = image_set.render_set.get_bigpages(zoom, pages)
                bigpage_set = range(1, bigpages + 1)
                subpages = image_set.render_set.get_subpages(zoom, pages)
                w = width / subpages_x
                h = height / subpages_y
                for bigpage in bigpage_set:
                    im_cmd = \
                        'montage %s-interlace PNG ' % opt_compress + \
                        '-background \%s ' % background  + \
                        '-geometry %dx%d+0+0 ' % (w, h) + \
                        '-tile %s ' % zoom
                    page_set = range((bigpage - 1) * subpages + 1, min(bigpage * subpages, pages) + 1)
                    for page in page_set:
                        png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                        im_cmd += '%s ' % png_ni_name
                    png_name = '%s_%s_%04d.png' % (pdf_fname, zoom, bigpage)                        
                    im_cmd += png_name
                    print im_cmd
                    os.system(im_cmd)
                    for page in page_set:
                        png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                        rm_cmd = 'rm %s' % png_ni_name
                        print rm_cmd
                        os.system(rm_cmd)
                    storage.store(png_name, bigpage, zoom)  # TODO remove png
