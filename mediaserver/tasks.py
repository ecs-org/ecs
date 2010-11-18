# -*- coding: utf-8 -*-

from celery.decorators import task

@task()
def rerender_pages(identifier=None, **kwargs):
    import tempfile, shutil
    from ecs.mediaserver.mediaprovider import MediaProvider
    from ecs.mediaserver.renderer import render_pages
    
    logger = rerender_pages.get_logger(**kwargs)
    logger.debug("rerender_pages called with identifier %s" % identifier)
    
    if identifier is None:
        logger.warning("Warning, rerender_pages(identifier is None)")
        return False, str(None), "identifier is none"
    
    mediaprovider = MediaProvider()
    try:
        filelike = mediaprovider.getBlob(identifier)
    except KeyError as exceptobj:
        logger.error("rerender_pages could not getBlob(%s), exception was %r" % (identifier, exceptobj))
        return False, str(identifier), repr(exceptobj)
    
    try:    
        render_dirname = tempfile.mkdtemp()
        
        for page, data in render_pages(identifier, filelike, render_dirname):
            mediaprovider.setPage(page, data, use_render_diskcache=True)
            if hasattr(data, "close"):
                data.close()
    
    except IOError as exceptobj:
        logger.error("render_pages of blob %s returned an IOError: %r" % (identifier, exceptobj))
        result = False, str(identifier), repr(exceptobj)
    else:
        result = True, str(identifier), ""
    finally:    
        shutil.rmtree(render_dirname)
        
    return result
