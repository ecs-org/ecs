# -*- coding: utf-8 -*-
from ecs import bootstrap
from django.conf import settings
from ecs.utils import gpgutils

@bootstrap.register()
def import_mediaserver_priv_key():
    keyfile = open(settings.MEDIASERVER_PRIV_KEY, 'rb')
    gpgutils.reset_keystore(settings.MEDIASERVER_GPG_HOME)
    gpgutils.import_key(keyfile, settings.MEDIASERVER_GPG_HOME)
