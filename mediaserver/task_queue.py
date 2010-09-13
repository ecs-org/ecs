from celery.decorators import task
# FIXME/mediaserver: from ecs.documents.models import Document

# FIXME/mediaserver: from ecs.mediaserver.storage import Cache
# FIXME/mediaserver: from ecs.mediaserver.renderer import Renderer
# FIXME/mediaserver: from ecs.mediaserver.imageset import ImageSet

@task()
def cache_and_render(document_pk, **kwargs):
    return # FIXME/mediaserver
    logger = cache_and_render.get_logger(**kwargs)
    try:
        document = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return False
    
    image_set = ImageSet(document_pk)
    logger.info("Imageset %s" % repr(image_set))
    if image_set.store('doc save', document.file.name, document.pages) is False:
        logger.error('cache_and_render: can not store ImageSet "%s"' % document_pk)
        return False

    renderer = Renderer()
    logger.info("renderer %s" % repr(renderer))
    renderer.render(image_set)
    cache = Cache()
    logger.info('rendered key "%s", set "%s"' % (cache.get_set_key(image_set.id), image_set.set_data))
