#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import sys

from ecs.core import paper_forms
from ecs.core.models import SubmissionForm

if sys.argv < 2:
    f = sys.stdin
else:
    f = open(sys.argv[1])

data = simplejson.loads(f.read())
f.close()

fields = [(x.number, x.name) for x in paper_forms.get_field_info_for_model(SubmissionForm)]
print fields


