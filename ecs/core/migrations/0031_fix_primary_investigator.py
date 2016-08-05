# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20160721_1545'),
    ]

    operations = [
        migrations.RunSQL('''
            with t as (
                update core_investigator inv
                set main = true
                from core_submissionform sf
                where inv.submission_form_id = sf.id and
                    sf.primary_investigator_id is null
                returning sf.id as sf_id, inv.id as inv_id
            )
            update core_submissionform sf
                set primary_investigator_id = t.inv_id
                from t
                where t.sf_id = sf.id;
        '''),
    ]
