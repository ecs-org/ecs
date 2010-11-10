# -*- coding: utf-8 -*-

from time import time
from django.conf import settings
from ecs.utils import s3utils

def generate_mediaurls(name, pages):
    tiles = settings.MS_SHARED ["tiles"]
    width = settings.MS_SHARED ["resolutions"]
    aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
    expiration_sec = settings.MS_SHARED ["url_expiration_sec"]
    
    baseurl = settings.MS_CLIENT ["url"]
    key_id = settings.MS_CLIENT ["key_id"]
    key_secret = settings.MS_CLIENT ["key_secret"]
    docshotData = [];
    
    for t in tiles:
        for w in width:
            tilepages = pages / (t*t)
            if pages % (t*t) > 0: tilepages += 1
             
            for pagenum in range(1, tilepages+1):
                bucket = "/mediaserver/%s/%dx%d/%d/%d/" % (name, t, t, w, pagenum)
                expires = int(time()) + expiration_sec
                h =  w * aspect_ratio
                docshotData.append({
                    'description': "Page: %d, Tiles: %dx%d, Width: %dpx" % (pagenum, t, t, w),
                    'url': s3utils.S3url(key_id, key_secret).createUrl(baseurl, bucket, '', key_id, expires), 
                    'page': pagenum, 
                    'tx': t,
                    'ty': t,
                    'width': w, 
                    'height': h,
                })
                pagenum += 1
    return docshotData
