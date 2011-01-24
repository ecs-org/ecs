# -*- coding: utf-8 -*-

from ecs.integration.windmillsupport import anonymous

@anonymous()
def test_login(client):
    client.click(id=u'id_username')
    client.type(text=u'windmill@example.org', id=u'id_username')
    client.click(id=u'id_password')
    client.type(text=u'shfnajwg9e', id=u'id_password')
    client.click(value=u'login')
    client.waits.forPageLoad(timeout=u'20000')

    client.waits.forElement(link=u'Logout', timeout=u'8000')
    client.click(link=u'Logout')
    client.waits.forPageLoad(timeout=u'20000')

            
