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
        logger.warning("Warning, identifier is None")
        return False
    
    mediaprovider = MediaProvider()
    filelike = mediaprovider.getBlob(identifier)
    render_dirname = tempfile.mkdtemp()
    
    for page, data in render_pages(identifier, filelike, render_dirname):
        mediaprovider.setPage(page, data, use_render_diskcache=True)
        if hasattr(data, "close"):
            data.close()
        
    shutil.rmtree(render_dirname)
    return True