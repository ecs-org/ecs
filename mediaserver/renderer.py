import subprocess
import tempfile
from ecs.mediaserver.models.DocumentModel import MediaBlob, Docshot
import os

class Renderer(object):
    def renderPDFMontage(self, uuid, filelike, width, tiles_x, tiles_y, aspect_ratio=1.41428, dpi=72, depth=8):
        margin_x = 0
        margin_y = 0
        
        if tiles_x > 1 and tiles_y > 1:
            margin_x = 4
            margin_y = 4

        height=width/aspect_ratio
        tile_width = (width / tiles_x) - margin_x
        tile_height = (height / tiles_y) - margin_y
        
        tmp_renderdir = tempfile.mkdtemp() 
        tmp_rendersrc = os.path.join(tmp_renderdir, 'pdf_' + uuid)
        tmp_docshot_prefix = os.path.join(tmp_renderdir, 'docshot_' + uuid + '_' + width + '_' + tiles_x + 'x' + tiles_y + '_')
         
        f_rendersrc = os.open(tmp_rendersrc, "wb");
        f_rendersrc.write(filelike);
        f_rendersrc.close();
           
        args = 'montage -geometry %dx%d+%d+%d -tile %dx%d -density %d -depth %d %s PNG:%s%%d' % (tile_height, tile_width,margin_x, margin_y,tiles_x, tiles_y, dpi, depth, tmp_rendersrc, tmp_docshot_prefix)
        popen = subprocess.Popen(args)

        if popen.returncode != 0:
            raise IOError('montage returned error code % i')

        pagenr = 0
        
        docshots = [ ds for ds in os.listdir(tmp_renderdir) if ds.startswith("docshot") ]
        
        for ds in docshots:
            yield(Docshot(MediaBlob(uuid=uuid), tiles_x, tiles_y, width, pagenr=pagenr+1), open(ds,"rb"))
