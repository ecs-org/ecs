import logging
from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from django.utils.importlib import import_module

logger = logging.getLogger(__name__)


class StartupMiddleware(object):
    def __init__(self):
        for path in getattr(settings, 'STARTUP_CALLS', ()):
            module, name = path.rsplit('.', 1)
            func = getattr(import_module(module), name)
            logger.info('startup %s' % path)
            func()

        raise MiddlewareNotUsed()