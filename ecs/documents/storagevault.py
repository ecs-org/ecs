'''
============
StorageVault
============

A Write Once, read many times key/value store featuring

* transparent encryption+signing for storing data, decryption+verify support for
  retrieving data

.. warning::
    TODO: because its not checked where potential all value data is read in
    memory, usage should be limited to something memory can support (eg. 500mb)

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

from django.conf import settings

from ecs.utils import gpgutils


def getVault():
    return StorageVault(settings.STORAGE_VAULT['dir'])


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
            settings.STORAGE_VAULT['gpghome'],
            settings.STORAGE_VAULT['encryption_uid'],
            settings.STORAGE_VAULT['signature_uid']
        )

    def __getitem__(self, identifier):
        return gpgutils.decrypt_verify(
            self._gen_path(identifier),
            settings.STORAGE_VAULT['gpghome'],
            settings.STORAGE_VAULT['encryption_uid'],
            settings.STORAGE_VAULT['signature_uid']
        )
