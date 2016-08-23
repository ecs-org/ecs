# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.http import QueryDict


def fix_sf_docstashes(apps, schema_editor):
    DocStash = apps.get_model('docstash', 'DocStash')

    stashes = DocStash.objects.filter(
        group='ecs.core.views.submissions.create_submission_form')

    for stash in stashes:
        if 'POST' in stash.value:
            post = QueryDict(stash.value['POST'], mutable=True)

            m = post.pop('subject_males', None)
            f = post.pop('subject_females', None)
            c = post.pop('subject_childbearing', None)

            post['subject_males'] = '2' if m else '3'
            if f and c:
                post['subject_females_childbearing'] = '0'
            elif f and not c:
                post['subject_females_childbearing'] = '1'
            elif not f and c:
                post['subject_females_childbearing'] = '2'
            else:
                post['subject_females_childbearing'] = '3'

            stash.value['POST'] = post.urlencode()
            stash.save()


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0009_adjust_checklist_docstashes'),
    ]

    operations = [
        migrations.RunPython(fix_sf_docstashes),
    ]
