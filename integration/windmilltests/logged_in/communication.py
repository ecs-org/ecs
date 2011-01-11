# -*- coding: utf-8 -*-
import cicero

from ecs.integration.windmilldecorators import logged_in


@logged_in()
def test_new_message(client, times=1):
    client.click(id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'20000')
    client.select(option=u'office1@example.org', id=u'userswitcher_input')
    client.click(link=u'Nachrichten')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Neue Nachricht', timeout=u'8000')


    for i in xrange(times):
        client.click(link=u'Neue Nachricht')
        client.click(id=u'id_subject')
        client.type(text=cicero.sentences(n=1, min=3, max=10)[0], id=u'id_subject')
        client.click(id=u'id_receiver')
        client.select(option=u'presenter1@example.org', id=u'id_receiver')
        client.click(id=u'id_text')
        client.type(text='\n'.join(cicero.sentences(n=5)), id=u'id_text')
        client.click(value=u'Abschicken')

    client.click(value=u'33')
    client.waits.forPageLoad(timeout=u'20000')
    client.select(option=u'---------', id=u'userswitcher_input')
    client.click(xpath=u"//select[@id='userswitcher_input']/option[1]")


def test_10_new_messages():
    test_new_message(times=10)


