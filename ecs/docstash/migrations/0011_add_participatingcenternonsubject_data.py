# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.http import QueryDict


def add_participatingcenternonsubject_data(apps, schema_editor):
    DocStash = apps.get_model('docstash', 'DocStash')

    docstashes = DocStash.objects.filter(
        group='ecs.core.views.submissions.create_submission_form')

    for docstash in docstashes:
        if 'POST' in docstash.value:
            post = QueryDict(docstash.value['POST'], mutable=True)
            post['participatingcenternonsubject-TOTAL_FORMS'] = 0
            post['participatingcenternonsubject-INITIAL_FORMS'] = 0
            post['participatingcenternonsubject-MIN_NUM_FORMS'] = 0
            post['participatingcenternonsubject-MAX_NUM_FORMS'] = 1000
            docstash.value['POST'] = post.urlencode()
            docstash.save(update_fields=['value'])


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0010_subject_male_female'),
    ]

    operations = [
        migrations.RunPython(add_participatingcenternonsubject_data),
    ]
