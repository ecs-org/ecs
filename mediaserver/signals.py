# -*- coding: utf-8 -*-

from ecs.mediaserver.imageset import cache_and_render


def document_post_save(sender, instance, signal, *args, **kwargs):
    if str(instance.mimetype) == 'application/pdf' and instance.pages:
        cache_and_render(instance)
