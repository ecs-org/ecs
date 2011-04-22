# -*- coding: utf-8 -*-
import os.path, tempfile, shutil

from django.conf import settings
from django.core.cache import cache

from celery.decorators import task

from ecs.utils.pathutils import tempfilecopy
from ecs.utils.pdfutils import pdf2pngs


LOCK_EXPIRE = 60 * 10 # Lock expires in 10 minutes


def _render_pages(identifier, filelike, private_workdir):
    ''' Generator that yields page, imagedata 
    for each tiles * resolution * pages
    '''
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


@task(track_started=True)
def do_rendering(identifier=None, mimetype='application/pdf', **kwargs):
    ''' loads blob, rerender pages (if application/pdf). returns success, identifier, response
    '''
    logger = do_rendering.get_logger(**kwargs)
    logger.debug("do_rendering called with identifier %s , mimetype %s" % (identifier, mimetype))
    
    if identifier is None:
        logger.warning("Warning, do_rendering (identifier is None)")
        return False, str(None), "identifier is none"

    from ecs.mediaserver.utils import MediaProvider
    mediaprovider = MediaProvider()
    
    lock_id = "%s-lock-render" % (identifier)
    # cache.add fails if if the key already exists
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    # memcache delete is very slow, but we have to use it to take advantage of using add() for atomic locking
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            logger.info("Lock %s acquired" % (lock_id))

            try:
                filelike = mediaprovider.getBlob(identifier)
            except KeyError as exceptobj:
                return False, '', repr(exceptobj)
            
            if mimetype!='application/pdf':
                result = True, str(identifier), ""
            else:
                try:    
                    render_dirname = tempfile.mkdtemp()
                    
                    for page, data in _render_pages(identifier, filelike, render_dirname):
                        mediaprovider.setPage(page, data, use_render_diskcache=True)
                        if hasattr(data, "close"):
                            data.close()
                except IOError as exceptobj:
                    result = False, str(identifier), repr(exceptobj)
                else:
                    result = True, str(identifier), ""
                finally:    
                    shutil.rmtree(render_dirname)        
        finally:
            release_lock()
        
        logger.debug("Lock %s released" % (lock_id))
        return result
    else:
        logger.warning("Warning, already in progress: do_rendering identifier %s , mimetype %s " % (identifier, mimetype))
        return False, str(identifier), "already in progress"
