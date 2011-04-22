# -*- coding: utf-8 -*-
from time import time
from urllib2 import urlopen
from cStringIO import StringIO

from django.conf import settings
from django.test.client import Client
from django.http import Http404

from ecs.utils import s3utils


def prime_mediaserver(uuid, mimetype='application/pdf', personalization=None, brand=False):
    ''' Returns tuple: Success:True/False,Response:Text '''   
    
    if settings.CELERY_ALWAYS_EAGER:
        # TODO: is hack to workaround urlopen of mediaserver on runserver
        from ecs.mediaserver.utils import MediaProvider
        m = MediaProvider()
        result, identifier, response = m.prime_blob(uuid, mimetype, wait=True)
        return result, response
    else:
        objid_parts = ['prepare', uuid, mimetype]
        objid = '/'.join(objid_parts) + '/'
    
        key_id = settings.MS_CLIENT ["key_id"]
        expires = int(time()) + settings.MS_SHARED['url_expiration_sec']
    
        s3url = s3utils.S3url(key_id, settings.MS_CLIENT['key_secret'])
        url= s3url.createUrl(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)

        f = urlopen(url)
        response = f.read()
        f.close()
        if not response == 'ok':
            return False, response
        

def download_from_mediaserver(uuid, filename, personalization=None, brand=False):
    ''' returns blob from mediaserver as data; Not used normal, 
    except you want to get the data for further processing, eg. export submission '''
    
    if settings.MS_CLIENT.get('same_host_as_server', False):
        from ecs.mediaserver.utils import MediaProvider
        return MediaProvider().getBlob(uuid)
    else:
        # TODO using urlopen and lot of data over the internet might go wrong: Add resilience
        f = urlopen(generate_media_url(uuid, filename, personalization=personalization, brand=brand))
        return f


def generate_media_url(uuid, filename, mimetype='application/pdf', personalization=None, brand=False):
    ''' returns a url that will allow a user to download this blob using this url for a specific time
    '''
    objid_parts = ['download', uuid, mimetype]
    if personalization:
        objid_parts += ['brand', personalization]
    elif brand:
        objid_parts += ['brand', "True"]
    objid_parts.append(filename)

    objid = '/'.join(objid_parts) + '/'

    key_id = settings.MS_CLIENT ["key_id"]
    expires = int(time()) + settings.MS_SHARED['url_expiration_sec']

    s3url = s3utils.S3url(key_id, settings.MS_CLIENT['key_secret'])
    return s3url.createUrl(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)


def generate_pages_urllist(uuid, pages):
    ''' returns a list of ('description', 'url', 'page', 'tx', 'ty', 'width', 'height')
    for every supported rendersize options for every page of the document with uuid
    '''
    tiles = settings.MS_SHARED ["tiles"]
    width = settings.MS_SHARED ["resolutions"]
    aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
    expiration_sec = settings.MS_SHARED ["url_expiration_sec"]
    
    baseurl = settings.MS_CLIENT ["server"]
    bucket = settings.MS_CLIENT ["bucket"]
    key_id = settings.MS_CLIENT ["key_id"]
    key_secret = settings.MS_CLIENT ["key_secret"]
    docshotData = [];
    
    for t in tiles:
        for w in width:
            tilepages = pages / (t*t)
            if pages % (t*t) > 0: tilepages += 1
             
            for pagenum in range(1, tilepages+1):
                objectid = "%s/%dx%d/%d/%d/" % (uuid, t, t, w, pagenum)
                expires = int(time()) + expiration_sec
                h =  w * aspect_ratio
                docshotData.append({
                    'description': "Page: %d, Tiles: %dx%d, Width: %dpx" % (pagenum, t, t, w),
                    'url': s3utils.S3url(key_id, key_secret).createUrl(baseurl, bucket, objectid, key_id, expires), 
                    'page': pagenum, 
                    'tx': t,
                    'ty': t,
                    'width': w, 
                    'height': h,
                })
                pagenum += 1
    return docshotData
