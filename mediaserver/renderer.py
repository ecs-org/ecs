import subprocess
import tempfile
import os
from uuid import UUID

from django.conf import settings

from ecs.utils.pathutils import which
from ecs.mediaserver.cacheobjects import MediaBlob, Docshot


MONTAGE_PATH = which('montage').next()
    
def renderPDFMontage(uuid, tmp_rendersrc, width, tiles_x, tiles_y):
    aspect_ratio = settings.MEDIASERVER_DEFAULT_ASPECT_RATIO
    dpi = settings.MEDIASERVER_DEFAULT_DPI
    depth = settings.MEDIASERVER_DEFAULT_DEPTH   
    margin_x = 0
    margin_y = 0
    
    #if tiles_x > 1 and tiles_y > 1:
    #    margin_x = 4
    #    margin_y = 4

    height = width * aspect_ratio
    tile_width = (width / tiles_x) - margin_x
    tile_height = (height / tiles_y) - margin_y

    
    tmp_renderdir = tempfile.mkdtemp() 
    tmp_docshot_prefix = os.path.join(tmp_renderdir, '%s_%s_%sx%s_' % (uuid, width, tiles_x, tiles_y)) + "%04d"
     
    args = '%s -verbose -geometry %dx%d+%d+%d -tile %dx%d -density %d -depth %d %s PNG:%s' % (MONTAGE_PATH, tile_width, tile_height, margin_x, margin_y,tiles_x, tiles_y, dpi, depth, tmp_rendersrc, tmp_docshot_prefix)
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate() # XXX: use communicate if stdout and/or stderr output could be larger than standard system buffer
    returncode = popen.returncode
    
    if returncode != 0:
        raise IOError('montage returned error code:%d %s' % (returncode, stdout))

    pagenr = 0
    
    for ds in sorted(os.listdir(tmp_renderdir)):
        dspath = os.path.join(tmp_renderdir, ds)
        pagenr += 1
        yield Docshot(MediaBlob(UUID(uuid)), tiles_x, tiles_y, width, pagenr), open(dspath,"rb")

def renderDefaultDocshots(pdfblob, filelike):
    tiles = settings.MEDIASERVER_TILES
    width = settings.MEDIASERVER_RESOLUTIONS
    
    # prepare the temporary render src
    tmp_rendersrc = tempfile.mktemp();
    with open(tmp_rendersrc, "wb") as f_rendersrc:
        f_rendersrc.write(filelike.read());

    for t in tiles:
        for w in width:
            for docshot, data in renderPDFMontage(pdfblob.cacheID(), tmp_rendersrc, w, t, t):
                yield docshot, data
