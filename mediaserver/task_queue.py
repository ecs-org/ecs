from celery.decorators import task
from ecs.core.models import Document

from ecs.mediaserver.storage import Cache
from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.imageset import ImageSet

@task()
def cache_and_render(document_pk):
    try:
        document = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        print("Warning, Document with pk %s does not exist" % str(document_pk))
        return
    image_set = ImageSet(document_pk)
    if image_set.store('doc save', document.file.name, document.pages) is False:
        print 'cache_and_render: can not store ImageSet "%s"' % document_pk
        return
    renderer = Renderer()
    renderer.render(image_set)
    cache = Cache()
    print 'rendered key "%s", set "%s"' % (cache.get_set_key(image_set.id), image_set.set_data)
