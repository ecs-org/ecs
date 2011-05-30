# -*- coding: utf-8 -*-
import os.path

from django.conf import settings

from ecs import bootstrap
from ecs.utils import gpgutils
from ecs.mediaserver.utils import MediaProvider

@bootstrap.register()
def import_decryption_verify_keys():
    gpgutils.reset_keystore(settings.STORAGE_DECRYPT ["gpghome"])
    if hasattr(settings.STORAGE_DECRYPT, "decrypt_key"):
        gpgutils.import_key(settings.STORAGE_DECRYPT ["decrypt_key"], settings.STORAGE_DECRYPT ["gpghome"])
    if hasattr(settings.STORAGE_DECRYPT, "verify_key"):
        gpgutils.import_key(settings.STORAGE_DECRYPT ["verify_key"], settings.STORAGE_DECRYPT ["gpghome"])

@bootstrap.register()
def import_encryption_sign_keys():
    gpgutils.reset_keystore(settings.STORAGE_ENCRYPT ["gpghome"])
    if hasattr(settings.STORAGE_ENCRYPT, "encrypt_key"):
        gpgutils.import_key(settings.STORAGE_ENCRYPT ["encrypt_key"], settings.STORAGE_ENCRYPT ["gpghome"])
    if hasattr(settings.STORAGE_ENCRYPT, "signing_key"):
        gpgutils.import_key(settings.STORAGE_ENCRYPT ["signing_key"], settings.STORAGE_ENCRYPT ["gpghome"])

@bootstrap.register()
def create_disk_caches():
    m = MediaProvider(allow_mkrootdir=True)

@bootstrap.register()
def create_local_storage_vault():
    workdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']
    if workdir:
        if not os.path.isdir(workdir):
            os.makedirs(workdir)
