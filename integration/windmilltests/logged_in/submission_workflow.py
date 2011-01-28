# -*- coding: utf-8 -*-
import os
import random
import cicero
from django.template.defaultfilters import slugify
from ecs.integration.windmillsupport import authenticated
from ecs.integration.windmilltests import create_submission


def select_user(client, email):
    client.select(option=email, id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')


def complete_task(client, option=None):
    option = u'id_action_complete%s' % ("_%s" % option if option is not None else "")
    client.waits.forElement(timeout=u'8000', id=u'workflow_button')
    client.click(id=u'workflow_button')
    client.waits.forElement(timeout=u'8000', id=option)
    client.click(id=option)
    client.radio(id=option)
    client.click(value=u'Abschicken')
    client.waits.forPageLoad(timeout=u'20000')


def click_task(client, ek, tasktype):
    client.click(jsid="$$('.ecs-Popup .tasks_%s a').filter(function(link){return link.innerHTML=='%s';})[0].id = 'next-windmill-task'" % (slugify(tasktype), ek))
    client.waits.forPageLoad(timeout=u'20000')


def open_workflow(client):
    client.click(id=u'workflow_button')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')
    client.waits.forElement(classname="ecs-Popup")


@authenticated()
def test_recordingSuite0(client):
    ek = create_submission(client)
    #ek = "1049/2011"
    print ek
    # reject
    select_user(client, u'office1@example.org')
    open_workflow(client)
    click_task(client, ek, 'Initial Review')
    click_task(client, ek, 'Initial Review')
    complete_task(client, 1) # reject
    
    # resubmit
    select_user(client, u'presenter1@example.org')
    open_workflow(client)
    click_task(client, ek, 'Resubmission')
    click_task(client, ek, 'Resubmission')
    client.waits.forElement(timeout=u'8000', id=u'submit-button')
    client.waits.sleep(milliseconds=u'5000')
    client.click(id=u'submit-button')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(timeout=u'8000', value=u'Ok')
    client.click(value=u'Ok')
    client.waits.forPageLoad(timeout=u'20000')
    open_workflow(client)
    complete_task(client)
    
    # accept
    select_user(client, u'office1@example.org')
    open_workflow(client)
    click_task(client, ek, 'Initial Review')
    click_task(client, ek, 'Initial Review')
    complete_task(client, 0)
    
    
