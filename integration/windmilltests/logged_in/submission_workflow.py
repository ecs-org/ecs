# -*- coding: utf-8 -*-
import os
import random
import cicero
from django.template.defaultfilters import slugify
from ecs.integration.windmillsupport import authenticated


class WorkflowTest(object):
    def __call__(self):
        @authenticated()
        def inner(client):
            return self.run(client)
        return inner()

    def run(self, client):
        raise NotImplementedError

    def select_user(self, client, email):
        client.select(option=email, id=u'userswitcher_input')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.sleep(milliseconds=u'5000')

    def open_workflow(self, client):
        client.click(id=u'workflow_button')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.sleep(milliseconds=u'5000')
        client.waits.forElement(classname="ecs-Popup")

    def click_task(self, client, ek, tasktype):
        client.execJS(js="$$('.ecs-Popup .tasks_{0} a').filter(function(link){{return link.innerHTML=='{1}';}})[0].id = 'windmill_next_task'".format(
            slugify(tasktype), ek))
        client.click(id='windmill_next_task')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.sleep(milliseconds=u'5000')

    def complete_task(self, client, option=None):
        option = u'id_action_complete%s' % ("_%s" % option if option is not None else "")
        client.waits.forElement(timeout=u'8000', id=u'workflow_button')
        client.click(id=u'workflow_button')
        client.waits.forElement(timeout=u'8000', id=option)
        client.click(id=option)
        client.radio(id=option)
        client.click(value=u'Abschicken')
        client.waits.forPageLoad(timeout=u'20000')


class SimpleTest(WorkflowTest):
    def run(self, client):
        from ecs.integration.windmilltests import create_submission
        ec_number = create_submission(client)

        # Initial Review
        self.select_user(client, u'office1@example.org')
        self.open_workflow(client)
        self.click_task(client, ec_number, 'Initial Review')
        self.click_task(client, ec_number, 'Initial Review')
        self.complete_task(client, 0)

        # Paper Submission Review
        self.select_user(client, u'office1@example.org')
        self.open_workflow(client)
        self.click_task(client, ec_number, 'Paper Submission Review')
        self.click_task(client, ec_number, 'Paper Submission Review')
        self.complete_task(client)

        # Categorization Review
        self.select_user(client, u'executive1@example.org')
        self.open_workflow(client)
        self.click_task(client, ec_number, 'Categorization Review')
        self.click_task(client, ec_number, 'Categorization Review')
        client.waits.forElement(timeout=u'8000', id=u'id_thesis')
        client.click(id=u'id_thesis')
        client.select(option=u'Nein', id=u'id_thesis')
        client.click(value=u'3')
        client.click(id=u'id_retrospective')
        client.select(option=u'Nein', id=u'id_retrospective')
        client.click(xpath=u"//select[@id='id_retrospective']/option[3]")
        client.click(xpath=u"//select[@id='id_medical_categories']/option[2]")
        client.click(xpath=u"//select[@id='id_medical_categories']/option[3]")
        client.click(value=u'4')
        client.click(id=u'id_expedited')
        client.select(option=u'Nein', id=u'id_expedited')
        client.click(xpath=u"//select[@id='id_expedited']/option[3]")
        client.click(id=u'id_external_reviewer')
        client.select(option=u'Nein', id=u'id_external_reviewer')
        client.click(xpath=u"//select[@id='id_external_reviewer']/option[3]")
        client.click(id=u'id_is_amg')
        client.click(xpath=u"//select[@id='id_is_amg']/option[3]")
        client.click(id=u'id_is_mpg')
        client.click(xpath=u"//select[@id='id_is_mpg']/option[3]")
        client.click(id=u'id_insurance_review_required')
        client.select(option=u'Nein', id=u'id_insurance_review_required')
        client.click(xpath=u"//select[@id='id_insurance_review_required']/option[3]")
        client.click(id=u'id_remission')
        client.select(option=u'Nein', id=u'id_remission')
        client.click(xpath=u"//select[@id='id_remission']/option[3]")
        client.click(value=u'Speichern')
        client.waits.forPageLoad(timeout=u'20000')
        self.complete_task(client)

test_simple_workflow = SimpleTest()


class ResubmitTest(WorkflowTest):
    def run(self, client):
        from ecs.integration.windmilltests import create_submission
        ek = create_submission(client)

        # reject
        self.select_user(client, u'office1@example.org')
        self.open_workflow(client)
        self.click_task(client, ek, 'Initial Review')
        self.click_task(client, ek, 'Initial Review')
        self.complete_task(client, 1) # reject

        # resubmit
        self.select_user(client, u'presenter1@example.org')
        self.open_workflow(client)
        self.click_task(client, ek, 'Resubmission')
        self.click_task(client, ek, 'Resubmission')
        client.waits.forElement(timeout=u'8000', id=u'submit-button')
        client.waits.sleep(milliseconds=u'5000')
        client.click(id=u'submit-button')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.forElement(timeout=u'8000', value=u'Ok')
        client.click(value=u'Ok')
        client.waits.forPageLoad(timeout=u'20000')
        self.open_workflow(client)
        self.complete_task(client)

        # accept
        self.select_user(client, u'office1@example.org')
        self.open_workflow(client)
        self.click_task(client, ek, 'Initial Review')
        self.click_task(client, ek, 'Initial Review')
        self.complete_task(client, 0)

        # paper review
        self.select_user(client, u'office1@example.org')
        self.open_workflow(client)
        self.click_task(client, ek, 'Paper Submission Review')
        self.click_task(client, ek, 'Paper Submission Review')
        self.complete_task(client)

test_resubmit_workflow = ResubmitTest()

