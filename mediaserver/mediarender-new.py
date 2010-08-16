
==utils==
  document_read_urls(uuid, validuntil)


==storagevault==
  put(uuid, hash, mimetype, filelike)
  (mimetype, hash, filelike) = get(uuid)
  secureurl_generate(secretkey, validuntil, url)
  secureurl_validate(publickey, url)

  
==mediaserver==

===lowlevel===
  document_getinfo(source)
    # returns mimetype, pages if pdf
  document_render(source, pixelwidth, targetnaming)
    # returns a bunch of png's
  document_montage()
    # returns a montage  
  document_stamp (source, dest, uuid, uuid)

===views===        
/ms/{uuid}/1x1/{pixelwidth(800,768,thumbnail)}/{pagenr(1..x)}
    # give one rendered page
/ms/{uuid}/{montagefactor(3x3,5x5)}/{pixelwidth(800,768)}/{pagenr}
    # give montaged overview page
/ms/{uuid}/download
    # give download of uuid stamped pdf 
/ms/{uuid}/download/original
    # give download of original file without touching it
/ms/{uuid}/download/uuidtostamp
    # give download of uuid stamped and second uuid stamped pdf

===Constants, should be put into settings, because independend parts need it (ms and ecs)
PW_800 = 800
PW_768 = 768
PW_3x3_800 = 800 / 3
PW_5x5_800 = 800 / 5
PW_3x3_768 = 768 / 3
PW_5x5_768 = 768 / 5
PW_thumbnail = 90
PW_ALL = (PW_800, PW_768, PW_3x3_800, PW_5x5_800, PW_3x3_768, PW_5x5_768)

===Classes===
class msdocument(object):
    def __init__(self, uuid):
        pass
    def info (self):    # or just msdocument(uuid))?
        pass
    def prepare(self, only_load_from_storage=False, allpagespixelwidths=PW_ALL, thumbnailwidth=PW_thumbnail):
        # if only_load_from_storage, document will only loaded from storage, no rendering will be done
        # defaults to file loaded from storage and put in doc_diskcache,
        #     all pages will be rendered and put into cache (where they will be put into diskcache)
        pass
    def pages(self, cols=1, rows=1):
        info = imagestore.info(uuid)
        pages_per_montage = (cols* rows)
        maxpage = info.pages Div pages_per_montage
        if info.pages mod pages_per_montage > 0:
            maxpage += 1
        return maxpage
    def _identifier(uuid, cols, rows, resolution, page):
        # return a identifier string for document uuid, cols, rows, resolution, page, to be used by others
        pass
    def get(self, fileuuid=True, requestuuid=None):
        # if fileuuid = True, then the uuid of the file will be stamped in before giving it. requestuuid will be stamped too if not None (second barcode)
        pass
    def __index_or_whatever_its_called__(self, indexnr):
        # msdocument[1..X].__get__ -> mspage object
        # creates a mspage object
        pass
        
class mspage(object):
    def __init__(self, documentobject, page):
        pass
    def image(self, pixelwidth=None):
        # tries to get uuid_1x1_pixelwidth_page.png from cache
        # if not, fallback to celery task render and put into cache, 
        #    and return a "processing, please wait" page , with expires in a view seconds
        pass
    def montage(self, cols=1, rows=1, pixelwidth=None):
        # * tries to get uuid_{cols}x{rows}_{pixelwidth}_{page}.png  from cache
        # * if not, tries to get for page in firstpage to lastpage of uuid_colsxrows_pixelwidth_ from cache (with NO_MEMCACHE=True)
        #   * where page > pages dont request it but put empty page as placeholder 
        #   * montage pictures together
        #   * put into cache
        #   * read from cache (puts it into memcache)
        # * if not, fallback to rerender seperate pages to diskcache, montage result and put into diskcache, memcache
        #   and return a "processing, please wait" page, with expires in a view seconds
        lastpage = page * cols * rows # eg. 2 * 3 * 3 = 18
        firstpage = lastpage - ((cols * rows)-1)
        pass
    

===caching===
  
class cache(object):
    max_doc_diskcache = 2**34 # 16 Gigabyte
    max_render_memcache = 2**29 # 512 Megabyte
    max_render_diskcache = 2**33 # 8 Gigabyte

    def __init__(self, doccachepath, rendercachepath, memcache):
    def get_document (self, uuid): # or better x= cache.document[uuid] 
        # get document from diskcache, will return filelike or string depending size
    def put_document (uuid, data): # or better cache.document[uuid] = x
        # put document to diskcache, data can be filelike, for bigfiles, or string 
    def get_info(self, uuid) # or better x= cache.info[uuid]
    def put_info(self, uuid, info) # or better cache.info[uuid] = x
 
    def get_page(self, identifier, diskcacheonly=False):  # or better x= cache.page[identifier] 
        # if diskcacheonly, then only search in diskcache, and dont put in memcache afterwards
        # else
        #    if found in memcache, take entry of memcache, touch lastaccesstime off diskcache
        #    if found in diskcache, take entry of diskcache, put in memcache, touch lastaccesstime off diskcache
    def put_page(self, identifier, data): # or better cache.page[identifier] = x
        # put in diskcache, doesnt put it in memcache
    def _age_doc_cache(self, max_doc_diskcache=None):
        # see age_cache
        pass
    def _age_render_cache(self, max_render_diskcache=None):
        # see age_cache
        pass
    def age_cache(self, max_doc_diskcache=None, max_render_diskcache=None):
        # does this for both doc_cache and render_cache
        # * find all files (but not info files) in cachedir (sorted by last accesstime) and sum all filesizes of cachedir
        #   * while sum > max_size
        #     * get next oldest file and delete it
        #     * update sum
        pass

    