# -*- coding: utf-8 -*-

import os
import tempfile
import subprocess
import logging

from django.conf import settings
from uuid import UUID
from ecs.utils.pathutils import which, tempfilecopy
from ecs.mediaserver.cacheobjects import Docshot, MediaBlob

MONTAGE_PATH = which('montage').next()

def pdf2pngs(uuid, tmp_rendersrc, width, tiles_x, tiles_y, aspect_ratio, dpi, depth):
    logger = logging.getLogger("renderer")
    
    margin_x = 0
    margin_y = 0   
    height = width * aspect_ratio
    tile_width = (width / tiles_x) - margin_x
    tile_height = (height / tiles_y) - margin_y

    tmp_renderdir = tempfile.mkdtemp() 
    tmp_docshot_prefix = os.path.join(tmp_renderdir, '%s_%s_%sx%s_' % (uuid, width, tiles_x, tiles_y)) + "%04d"
     
    args = [MONTAGE_PATH, "-verbose", "-geometry", "%dx%d+%d+%d" % (tile_width, tile_height, margin_x, margin_y),
        "-tile", "%dx%d" % (tiles_x, tiles_y), "-density", "%d" % dpi, "-depth", "%d" % depth,
        tmp_rendersrc, "PNG:%s" % tmp_docshot_prefix]
    
    popen = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    logger.debug("Started montage under %s , with args %s " % (str(popen), str(args)))
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        raise IOError('montage returned error code:%d %s' % (returncode, stdout))

    pagenr = 0
    for ds in sorted(os.listdir(tmp_renderdir)):
        dspath = os.path.join(tmp_renderdir, ds)
        pagenr += 1
        yield Docshot(MediaBlob(UUID(uuid)), tiles_x, tiles_y, width, pagenr), open(dspath,"rb")

def renderDefaultDocshots(pdfblob, filelike):
    tiles = settings.MS_SHARED ["tiles"]
    width = settings.MS_SHARED ["resolutions"]
    aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
    dpi = settings.MS_SHARED ["dpi"]
    depth = settings.MS_SHARED ["depth"]   
    
    copied_file = False   
    if hasattr(filelike,"name"):
        tmp_rendersrc = filelike.name
    elif hasattr(filelike, "read"):
        tmp_rendersrc = tempfilecopy(filelike)
        copied_file = True
    
    try:   
        for t in tiles:
            for w in width:
                for docshot, data in pdf2pngs(pdfblob.cacheID(), tmp_rendersrc, w, t, t, aspect_ratio, dpi, depth):
                    yield docshot, data
    finally:
        if copied_file:
            if os.path.exists(tmp_rendersrc):
                os.remove(tmp_rendersrc)
            
        
