
==utils==
document_read_urls(uuid, validuntil)


==storagevault==
  put(uuid, hash, mimetype, filelike)
  (mimetype, hash, filelike) = get(uuid)
  secureurl_generate(secretkey, validuntil, url)
  secureurl_validate(publickey, url)

==mediaserver==

PW_800 = 800
PW_768 = 768
PW_3x3_800 = 800 / 3
PW_5x5_800 = 800 / 5
PW_3x3_768 = 768 / 3
PW_5x5_768 = 768 / 5
PW_thumbnail = 90
PW_ALL = (PW_800, PW_768, PW_3x3_800, PW_5x5_800, PW_3x3_768, PW_5x5_768)

class msdocument(object):
    def __init__(self, uuid):
        pass
    def info ():    # or just document(uuid))
        pass
    def prepare(only_load_from_storage=False, allpagespixelwidths=PW_ALL, thumbnailwidth=PW_thumbnail):
        pass
    def pages(cols=1, rows=1):
        info = imagestore.info(uuid)
        pages_per_montage = (montagex* montagey)
        maxpage = info.pages Div pages_per_montage
        if info.pages mod pages_per_montage > 0:
            maxpage += 1
        return maxpage
    def get(fileuuid=True, requestuuid=None):
        pass
    def __index__(indexnr):
        # [1..X].__get__ -> page object
        pass
        
class mspage(object):
    def __init__(self, documentobject, page)        
    def montage(cols=1, rows=1, pixelwidth=None)
    def image(pixelwidth=None)
    
lowlevel

document_getinfo(source)
document_render(source)
document_montage()
document_stamp (source, dest, uuid, uuid)


caching
  
cache
  max_doc_diskcache
  max_render_memcache
  max_render_diskcache
  
  get_document (uuid)
  put_document (uuid, data)
  
  get_info(uuid)
  put_info(uuid, info)
  
  get_page(uuid, resolution=None, page=None, cols=None, rows=None)
  put_page(uuid, resolution=None, page=None, cols=None, rows=None)
  put_page_mem(-,,-)

  _age_doc_cache
  _age_render_cache
  age_cache

    
/ms/uuid/resolutionx(800,768)/pagenr(1..x)
    info = imagestore.info(uuid)
    if not info:
        imagestore.render(uuid)
    if info.pages < pagenr
        return HttpResponseError("page does not exist")
    pageimg = memcache.get("%s-%s-%s" % uuid, resolution, pagenr)
    if not pageimg:
        pageimg = imagestore.get(uuid, resolution, pagenr)
    
 /ms/uuid/montage/montagefactor(3x3,5x5)/pagenr
    info = imagestore.info(uuid)
    if not info:
        imagestore.render(uuid)
    if info.pages div (montagex*montagey) < pagenr*montagex*montagey
        return HttpResponseError("page does not exist")
    
    info = memcache.get("%s-info" 
 /ms/uuid/download
 /ms/uuid/download/singleid
 /ms/uuid/download/doubleid/uuidtostamp
