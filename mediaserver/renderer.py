import os

from ecs.mediaserver.storage import Storage

class Renderer(object):
    def render(self, pdf_name, image_set):
        storage = Storage()
        pages = image_set.pages  # TODO use PyPDF to get page number
        background = '#dddddd'
        for zoom in image_set.images:
            print '%s: ' % zoom,
            if zoom == '1':  # TODO calc from zoom dimensions
                res_x = 96.762
                res_y = 96.725
            elif zoom == '3x3':
                res_x = 32.173
                res_y = 32.242
            elif zoom == '5x5':
                res_x = 19.352
                res_y = 19.345
            pdf_fname, _ = os.path.splitext(os.path.basename(pdf_name))
            gs_cmd = \
                'gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dGraphicsAlphaBits=4 ' + \
                '-dPDFFitPage -dTextAlphaBits=4 -sPAPERSIZE=a4 ' + \
                '-r%sx%s ' % (res_x, res_y) + \
                '-dFirstPage=1 -dLastPage=%s ' % pages + \
                '-sOutputFile=%s_%s_%%04d_ni.png ' % (pdf_fname, zoom) + \
                pdf_name
            print gs_cmd
            os.system(gs_cmd)
            if zoom == '1':
                for page in image_set.images[zoom]:
                    png_ni_name = '%s_%s_%04d_ni.png' % (pdf_fname, zoom, page)
                    png_name = '%s_%s_%04d.png' % (pdf_fname, zoom, page)
                    im_cmd = 'convert -interlace PNG %s %s' % (png_ni_name, png_name)
                    print im_cmd
                    os.system(im_cmd)
                    rm_cmd = 'rm %s' % png_ni_name
                    print rm_cmd
                    os.system(rm_cmd)
                    storage.store(png_name, page, zoom)  # TODO remove png
            else:
                bigpages = image_set.render_set.get_bigpages(zoom, pages)
                print "bigpages = %s" % bigpages
                bigpage_set = range(1, bigpages + 1)
                if zoom == '3x3':  # TODO calc
                    w = 266
                    h = 377
                else:
                    w = 160
                    h = 226
                for bigpage in bigpage_set:
                    im_cmd = \
                        'montage -interlace PNG ' + \
                        '-background \%s ' % background  + \
                        '-geometry %sx%s+0+0 ' % (w, h) + \
                        '-tile %s ' % zoom
                    for page in image_set.images[zoom]:
                        png_ni_name = '%s_%s_%04d_ni.png ' % (pdf_fname, zoom, page)
                        im_cmd += '%s ' % png_ni_name
                    png_name = '%s_%s_%04d.png' % (pdf_fname, zoom, bigpage)                        
                    im_cmd += png_name
                    print im_cmd
                    os.system(im_cmd)
                    for page in image_set.images[zoom]:
                        png_ni_name = '%s_%s_%04d_ni.png ' % (pdf_fname, zoom, page)
                        rm_cmd = 'rm %s' % png_ni_name
                        print rm_cmd
                        os.system(rm_cmd)
                    storage.store(png_name, bigpage, zoom)  # TODO remove png
