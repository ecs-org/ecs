# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.http import QueryDict


def fix_categorization_docstashes(apps, schema_editor):
    DocStash = apps.get_model('docstash', 'DocStash')

    stashes = DocStash.objects.filter(
        group='ecs.core.views.submissions.categorization')

    for stash in stashes:
        if 'POST' in stash.value:
            post = QueryDict(stash.value['POST'], mutable=True)

            post.pop('gcp_review_required', None)
            post.pop('insurance_review_required', None)
            post.pop('external_reviewers', None)
            post.pop('statistical_review_required', None)
            post.pop('legal_and_patient_review_required', None)
            post.pop('expedited_review_categories', None)
            post.pop('executive_comment', None)

            if 'workflow_lane' in post and not post['workflow_lane']:
                post.pop('workflow_lane')

            if post.getlist('medical_categories') in ([], ['']):
                post.pop('medical_categories')

            if 'remission' in post and post['remission'] == 'False':
                post.pop('remission')

            if list(post.keys()) == ['csrfmiddlewaretoken']:
                stash.delete()
            else:
                stash.value['POST'] = post.urlencode()
                stash.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160929_1229'),
        ('docstash', '0010_subject_male_female'),
    ]

    operations = [
        migrations.RunPython(fix_categorization_docstashes),
    ]
