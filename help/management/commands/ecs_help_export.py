import sys, os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

from ecs.help.models import Page
from ecs.help.utils import Linker


class Command(BaseCommand):
    def handle(self, targetdir=None, **options):
        linker = Linker(
            image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
            doc_roles=False,
        )
        targetdir = settings.ECSHELP_ROOT if targetdir is None else targetdir
        src_dir = os.path.join(targetdir, 'src')
        try:
            os.makedirs(src_dir)
        except:
            pass

        for page in Page.objects.all():
            name = (slugify(page.slug) or ("page_%03d" % page.pk)) + '.rst'
            with open(os.path.join(src_dir, name), 'w') as f:
                f.write(linker.link(page.text).encode('utf-8'))
        

