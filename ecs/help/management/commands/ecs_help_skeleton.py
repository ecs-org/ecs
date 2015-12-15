import re
from reversion import revision

from django.core.management.base import BaseCommand
from django.core import urlresolvers
from django.conf import settings

from ecs.tracking.models import View
from ecs.help.models import Page

def _create_all_views(resolver):
    if not hasattr(resolver.urlconf_name, 'startswith') or not resolver.urlconf_name.startswith('ecs.'):
        return
    for pattern in resolver.url_patterns:
        if isinstance(pattern, (urlresolvers.RegexURLResolver,)):
            _create_all_views(pattern)
            continue
        callback = pattern._get_callback()
        if hasattr(callback, '__module__') and hasattr(callback, '__name__'):
            if not callback.__module__.startswith('ecs.') or callback.__name__ == '<lambda>':
                continue
            if hasattr(callback, 'tracking_hints') and callback.tracking_hints.get('exclude', False):
                continue
            View.objects.get_or_create(path='{0}.{1}'.format(callback.__module__, callback.__name__))

class Command(BaseCommand):
    def handle(self, **options):
        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.get_resolver(urlconf)

        _create_all_views(resolver)

        for v in View.objects.exclude(pk__in=Page.objects.filter(view__isnull=False).values('view').query):
            slug = re.sub(r'ecs\.(.*)\.views\.(.*)', r'\1.\2', v.path)
            with revision:
                Page.objects.create(view=v, slug=slug, title='Skeleton: {0}'.format(slug), text='Ich bin ein dummy!')
