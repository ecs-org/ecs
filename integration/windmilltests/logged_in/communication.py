# -*- coding: utf-8 -*-
import cicero

from ecs.integration.windmillsupport import authenticated


@authenticated()
def test_new_thread(client):
    client.click(id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'20000')
    client.select(option=u'presenter1@example.org', id=u'userswitcher_input')

    subject = cicero.sentences(n=1, min=3, max=10)[0]


    # new thead
    client.click(link=u'Nachrichten')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Neue Nachricht', timeout=u'8000')
    client.click(link=u'Neue Nachricht')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', id=u'id_subject')
    client.click(id=u'id_subject')
    client.type(text=subject, id=u'id_subject')
    client.click(id=u'id_text')
    client.type(text='\n'.join(cicero.sentences(n=5)), id=u'id_text')
    client.click(value=u'Abschicken')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', id=u'headertitle')
    client.click(id=u'headertitle')

    # bump
    client.click(id=u'id_text')
    client.type(text='\n'.join(cicero.sentences(n=5)), id=u'id_text')
    client.click(value=u'Abschicken')
    client.waits.forPageLoad(timeout=u'20000')

    client.click(id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'20000')
    client.select(option=u'office1@example.org', id=u'userswitcher_input')

    # answer
    client.click(link=u'Nachrichten')
    client.waits.forPageLoad(timeout=u'20000')
    client.click(link=subject)
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', id=u'id_text')
    client.click(id=u'id_text')
    client.type(text='\n'.join(cicero.sentences(n=5)), id=u'id_text')
    client.click(value=u'Abschicken')
    client.waits.forPageLoad(timeout=u'20000')

    client.select(option=u'---------', id=u'userswitcher_input')
    client.click(xpath=u"//select[@id='userswitcher_input']/option[1]")

