# -*- coding: utf-8 -*-
from ecs import bootstrap
from django.conf import settings
from ecs.utils import gpgutils

@bootstrap.register()
def import_decryption_key():
    gpgutils.reset_keystore(settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["key"], settings.STORAGE_DECRYPT ["gpghome"])
    