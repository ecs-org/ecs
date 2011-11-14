# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ecs import bootstrap
from ecs.utils import gpgutils
from ecs.mediaserver.utils import MediaProvider

@bootstrap.register()
def import_encryption_sign_keys():
    if not hasattr(settings, 'STORAGE_ENCRYPT'):
        raise ImproperlyConfigured("no STORAGE_ENCRYPT setting")
    for a in "gpghome", "encrypt_key", "signing_key":
        if not settings.STORAGE_ENCRYPT.has_key(a):
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_ENCRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["encrypt_key"], settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["signing_key"], settings.STORAGE_ENCRYPT ["gpghome"])

@bootstrap.register()
def import_decryption_verify_keys():
    if not hasattr(settings, 'STORAGE_DECRYPT'):
        raise ImproperlyConfigured("no STORAGE_DECRYPT setting")
    for a in "gpghome", "decrypt_key", "verify_key":
        if not settings.STORAGE_DECRYPT.has_key(a):
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_DECRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["decrypt_key"], settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["verify_key"], settings.STORAGE_DECRYPT ["gpghome"])

@bootstrap.register()
def create_disk_caches():
    m = MediaProvider(allow_mkrootdir=True)

@bootstrap.register()
def create_local_storage_vault():
    workdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']
    if workdir:
        if not os.path.isdir(workdir):
            os.makedirs(workdir)
