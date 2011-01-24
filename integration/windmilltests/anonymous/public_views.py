# -*- coding: utf-8 -*-

from ecs.integration.windmillsupport import anonymous

@anonymous()
def catalog(client):
    client.click(link=u'\xd6ffentliches Register')
    client.waits.forPageLoad(timeout=u'20000')

