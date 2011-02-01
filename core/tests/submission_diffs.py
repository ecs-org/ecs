# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from ecs.utils.testcases import EcsTestCase
from ecs.core.diff import diff_submission_forms
from ecs.core.tests.submissions import create_submission_form


class SubmissionFormDiffTest(EcsTestCase):
    def setUp(self, *args, **kwargs):
        rval = super(SubmissionFormDiffTest, self).setUp(*args, **kwargs)
        self.old_sf = create_submission_form()
        self.new_sf = create_submission_form()

        # both submission forms have to belong to the same submission
        self.new_sf.submission.current_submission_form = None
        self.new_sf.submission.save()
        self.new_sf.submission = self.old_sf.submission
        self.new_sf.save()

        return rval

    def test_submission_form_diff(self):
        self.new_sf.project_title = 'roflcopter'
        diff = diff_submission_forms(self.old_sf, self.new_sf)
        self.failUnless(diff[u'1.1 %s' % _('project title (english)')])
        self.failUnlessEqual(diff[u'1.1 %s' % _('project title (english)')].new, 'roflcopter')
