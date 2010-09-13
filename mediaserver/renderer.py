# -*- coding: utf-8 -*-

import subprocess
from ecs.mediaserver.models.DocumentModel import DocshotModel

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

        args = 'montage -geometry %dx%d+%d+%d -tile %dx%d -density %d -depth %d - PNG:-' % (tile_height, tile_width,margin_x, margin_y,tiles_x, tiles_y, dpi, depth)
        popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        raw_pngstream, stderr = popen.communicate(filelike)

        if popen.returncode != 0:
            raise IOError('montage returned error code % i , stderr: % s' % (popen.returncode, stderr))

        docshots = []
        pagenr = 0
        for png_data in self._split_raw_pngstream(raw_pngstream):
            docshots.append(DocshotModel(tiles_x, tiles_y, width, pagenr, uuid=uuid, data=png_data))
            pagenr = pagenr + 1

        return docshots

    def _split_raw_pngstream(self, raw_pngstream):
        import binascii
        header = binascii.a2b_hex('89504E470D0A1A0A')
        offsets = []
        last_offset = 0
        raw_pngs = []
    
        while True:
            offset = raw_pngstream.find(header, last_offset)
            if offset == -1:
                break
            offsets.append(offset)
            last_offset = offset + 1
    
        for i in xrange(len(offsets) - 1):
            start = offsets[i]
            end = offsets[i+1]
            raw_pngs.append(raw_pngstream[start:end])
    
        raw_pngs.append(raw_pngstream[offsets[-1]:])
    
        return raw_pngs 
