'''
Created on Aug 29, 2010

@author: elchaschab
'''
import time

def generate_mediaserver_urls(base_url, uuid, pages=(1,2,3), zoomlevels = (10,50,100), validforsec=25800):
    url_dict = {};
    for page in pages:
        for level in zoomlevels:
            url_dict['uuid: %s page: %s zoom: %s' % (uuid, page, level)] = '%s/%s/1x1/%s/%s?validuntil=%s' % (base_url, uuid, level, page, float(time.time()) + float(validforsec))
            
    return url_dict
                
        