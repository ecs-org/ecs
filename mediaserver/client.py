# -*- coding: utf-8 -*-
from time import time
from urllib2 import urlopen

from django.conf import settings

from ecs.mediaserver.utils import AuthUrl, MediaProvider


def add_to_storagevault(uuid, filelike): 
    ''' add (create or fail) a blob in the storage vault
    '''
    m = MediaProvider()
    m.add_blob(uuid, filelike)


def download_from_mediaserver(uuid, filename, personalization=None, brand=False):
    ''' :returns: blob from mediaserver as data; seldom usage.
    
    :see: generate_media_url() if you just want to pass access safely through the media server temporary urls
    :note: you may want this if you need the data for further processing, eg. export submission
    '''
    if settings.MS_CLIENT.get('same_host_as_server', False):
        from ecs.mediaserver.utils import MediaProvider
        return MediaProvider().get_blob(uuid)
    else:
        # TODO using urlopen and lot of data over the internet might go wrong: Add resilience
        f = urlopen(generate_media_url(uuid, filename, personalization=personalization, brand=brand))
        return f


def generate_media_url(uuid, filename, mimetype='application/pdf', personalization=None, brand=False):
    ''' :returns:  url that will allow a user to download this blob by using this url for a specific time period
    '''
    objid_parts = ['download', uuid, mimetype]
    if personalization:
        objid_parts += ['brand', personalization]
    elif brand:
        objid_parts += ['brand', "True"]
    objid_parts.append(filename)

    objid = '/'.join(objid_parts) + '/'

    key_id = settings.MS_CLIENT["key_id"]
    expires = int(time()) + settings.MS_CLIENT['url_expiration_sec']

    authurl = AuthUrl(key_id, settings.MS_CLIENT['key_secret'])
    return authurl.grant(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)
