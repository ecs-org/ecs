'''
Created on 11.10.2010

@author: felix
'''
from time import time

from django.conf import settings

from ecs.utils import s3utils
from ecs.documents.models import Document


def createmediaurls(document):
    cacheid = document.uuid_document
    tiles = settings.MEDIASERVER_TILES
    width = settings.MEDIASERVER_RESOLUTIONS 
    docshotData = [];
    
    for t in tiles:
        for w in width:
            for pagenum in range(1, document.pages+1):
                bucket = "/mediaserver/%s/%dx%d/%d/%d/" % (cacheid, t, t, w, pagenum)
                baseurl = settings.MEDIASERVER_URL
                expire = int(time()) + settings.S3_DEFAULT_EXPIRATION_SEC
                linkdesc = "Page: %d, Tiles: %dx%d, Width: %dpx" % (pagenum, t, t, w)
                h =  w * settings.MEDIASERVER_DEFAULT_ASPECT_RATIO
                # "linkdescription": ["expiringURL", page, tiles_x, tiles_y, width, height]
                docshotData.append({
                    'description': linkdesc,
                    'url': s3utils.createExpiringUrl(baseurl, bucket, '', settings.S3_DEFAULT_KEY, expire), 
                    'page': pagenum, 
                    'tx': t,
                    'ty': t,
                    'width': w, 
                    'height': h,
                })
                pagenum += 1
    
    return docshotData