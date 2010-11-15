# -*- coding: utf-8 -*-

import os

from django.conf import settings

from ecs.utils.pathutils import tempfilecopy
from ecs.utils.pdfutils import pdf2pngs


def render_pages(identifier, filelike, private_workdir):
    tiles = settings.MS_SHARED ["tiles"]
    resolutions = settings.MS_SHARED ["resolutions"]
    aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
    dpi = settings.MS_SHARED ["dpi"]
    depth = settings.MS_SHARED ["depth"]   
    
    copied_file = False   
    if hasattr(filelike,"name"):
        tmp_sourcefilename = filelike.name
    elif hasattr(filelike, "read"):
        tmp_sourcefilename = tempfilecopy(filelike)
        copied_file = True
    
    try:   
        for t in tiles:
            for w in resolutions:
                for page, data in pdf2pngs(identifier, tmp_sourcefilename, private_workdir, w, t, t, aspect_ratio, dpi, depth):
                    yield page, data
    finally:
        if copied_file:
            if os.path.exists(tmp_sourcefilename):
                os.remove(tmp_sourcefilename)
