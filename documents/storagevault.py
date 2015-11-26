# -*- coding: utf-8 -*-
'''
============
StorageVault
============

A Write Once, read many times key/value store featuring

* transparent encryption+signing for storing data, decryption+verify support for retrieving data
* easy to extent base class (StorageVault) for writing other StorageVault backend connectors
* simple local machine implementation (LocalFileStorageVault) using diskbuckets

.. warning::
    TODO: because its not checked where potential all value data is read in memory, usage should be limited to something memory can support (eg. 500mb)

Usage
=====

.. code-block:: python

    vault = getVault() # get configured vault

    vault[identifier] = filelike
    # adds the contents of filelike using identifier as key to the vault

    filelike = vault[identifier]
    # get a temporary copy of content using identifier as key accessible using filelike
'''

import os
import errno
import tempfile

from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from ecs.utils import gpgutils


def _aggressive_mkdtemp(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
    return tempfile.mkdtemp(dir=dir)


def getVault():
    ''' get the default vault implementation

    :raise ImproperlyConfigured: if settings.STORAGE_VAULT contains invalid storagevault implementation
    '''
    module, class_name = settings.STORAGE_VAULT.rsplit('.', 1)
    try:
        vault = getattr(import_module(module), class_name)
    except ImportError:
        raise ImproperlyConfigured("No Vault implementation for name: %s" % (settings.STORAGE_VAULT))
    return vault()


class StorageVault(object):
    ''' base class for a write once, read many times storage vault

    Features: on the fly Encryption+Signing, Decryption+Verifying
    '''
    def __init__(self, root_dir, max_depth=5):
        self.root_dir = os.path.abspath(root_dir)
        self.max_depth = max_depth

    def _gen_path(self, identifier):
        assert len(identifier) >= self.max_depth
        subdir = os.path.join(*identifier[:self.max_depth-1])
        return os.path.join(self.root_dir, subdir, identifier)

    def __setitem__(self, identifier, f):
        path = self._gen_path(identifier)
        assert not os.path.exists(path)

        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            if not e.errno == errno.EEXIST:
                raise

        gpgutils.encrypt_sign(
            f, path,
            settings.STORAGE_ENCRYPT['gpghome'],
            settings.STORAGE_ENCRYPT['encrypt_owner'],
            settings.STORAGE_ENCRYPT['signing_owner']
        )

    def __getitem__(self, identifier):
        return gpgutils.decrypt_verify(
            self._gen_path(identifier),
            settings.STORAGE_DECRYPT['gpghome'],
            settings.STORAGE_DECRYPT['decrypt_owner'],
            settings.STORAGE_DECRYPT['verify_owner']
        )


class LocalFileStorageVault(StorageVault):
    ''' StorageVault implementation using a local file storage

    :requires: settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']
    '''
    def __init__(self):
        super(LocalFileStorageVault, self).__init__(
            settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir'])


class TemporaryStorageVault(LocalFileStorageVault):
    ''' StorageVault implementation using a temporary storage inside tempdir (for unittests only)

    makes a temporary storagevault under a subdir of settings.TEMPFILE_DIR

    :requirements: to be used, settings.STORAGE_VAULT need to be set to "ecs.documents.storagevault.TemporaryStorageVault"
    '''

    # we initialize _TempStorageDir here, so we should become the same directory on each instantiation
    __TempStorageDir = _aggressive_mkdtemp(dir=settings.TEMPFILE_DIR)

    def __init__(self):
        root_dir = self.__TempStorageDir
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)
        super(TemporaryStorageVault, self).__init__(root_dir)
