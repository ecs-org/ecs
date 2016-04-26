# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import json
import pickle
import struct
import zlib

from django.db import migrations, models


def _model_form_unpickle(module, cls_name, args, kwargs):
    assert((module, cls_name) in (
        ('ecs.core.forms.forms', 'SubmissionFormForm'),
        ('ecs.core.forms.review', 'CategorizationReviewForm'),
        ('ecs.notifications.forms', 'SafetyNotificationForm'),
        ('ecs.notifications.forms', 'ProgressReportNotificationForm'),
        ('ecs.notifications.forms', 'CompletionReportNotificationForm'),
        ('ecs.notifications.forms', 'AmendmentNotificationForm'),
    ))
    assert(args == ())
    assert(kwargs['prefix'] is None)
    del kwargs['prefix']
    if kwargs['data']:
        kwargs['data'] = kwargs['data'].urlencode()
    return kwargs


def _model_formset_unpickle(name, args, kwargs):
    assert(name.endswith('FormSet'))
    assert(args == ())
    del kwargs['prefix']
    if kwargs['data']:
        kwargs['data'] = kwargs['data'].urlencode()
    return kwargs


def _checklist_form_unpickle(checklist_pk, args, kwargs):
    assert(args == ())
    assert(kwargs['prefix'] is None)
    del kwargs['prefix']
    kwargs['checklist_pk'] = checklist_pk
    if kwargs['data']:
        kwargs['data'] = kwargs['data'].urlencode()
    return kwargs


def _model_unpickle(model, args, factory):
    assert(model == None)
    assert(args == [])
    class FakeModel(object):
        pass
    return FakeModel()


class _ModelState(object):
    pass


def fix_2to3(apps, schema_editor):
    DocStashData = apps.get_model('docstash', 'DocStashData')
    datas = DocStashData.objects.filter(version=models.F('stash__current_version'))
    if not datas:
        return

    from picklefield.fields import PickledObject

    for data in datas:
        value = zlib.decompress(base64.b64decode(data.value))

        # Replace all binary datetime strings with tuple datetimes. We try to
        # detect binary datetimes by looking for strings of length 10, that
        # start with \x07 and are followed by \x85 (TUPLE1). This is a very
        # naive heuristic, but it seems to work for all docstashes we have in
        # the production system.

        i = 0
        while True:
            try:
                i = value.index(b'U\x0a\x07', i)
            except ValueError:
                break

            assert(value[i:i + 2] == b'U\x0a')
            assert(value[i + 12] == ord(b'\x85'))

            Y, M, D, h, m, s, *u = struct.unpack('>HBBBBBBH', value[i + 2: i + 12])
            new = pickle.dumps((Y, M, D, h, m, s, (u[0] << 16) + u[1]))
            assert(new[:2] == b'\x80\x03')
            assert(new[-3:] == b'q\x00.')
            new = new[2:-3]   # strip container

            value = value[:i] + new + value[i + 13:]
            i += 13


        # Force all composite objects in the serialized data to be loaded as
        # plain python objects.

        value = value.replace(
            b'cecs.utils.formutils\n_unpickle\n',
            b'cecs.docstash.migrations.0005_fix_2to3\n_model_form_unpickle\n'
        ).replace(
            b'cecs.core.forms.forms\n_unpickle\n',
            b'cecs.docstash.migrations.0005_fix_2to3\n_model_formset_unpickle\n'
        ).replace(
            b'cdjango.db.models.base\nmodel_unpickle\n',
            b'cecs.docstash.migrations.0005_fix_2to3\n_model_unpickle\n'
        ).replace(
            b'cecs.notifications.models\nNotificationType\n',
            b'N'
        ).replace(
            b'cecs.core.models.submissions\nSubmission\n',
            b'N'
        ).replace(
            b'cecs.core.models.submissions\nSubmissionForm\n',
            b'N'
        ).replace(
            b'cdjango.db.models.base\nsimple_class_factory\n',
            b'N'
        ).replace(
            b'cdjango.db.models.base\nModelState\n',
            b'cecs.docstash.migrations.0005_fix_2to3\n_ModelState\n'
        ).replace(
            b'cecs.checklists.forms\n_unpickle\n',
            b'cecs.docstash.migrations.0005_fix_2to3\n_checklist_form_unpickle\n'
        )

        value = pickle.loads(value, encoding='utf-8')

        if data.stash.group == 'ecs.core.views.submissions.categorization_review':
            if value['form']['data']:
                value = {'POST': value['form']['data']}
            else:
                value = {}
        elif data.stash.group == 'ecs.core.views.submissions.checklist_review':
            if value['form']['data']:
                value = {'POST': value['form']['data']}
            else:
                value = {}
        elif data.stash.group == 'ecs.notifications.views.create_notification':
            v = {
                'type_id': value['type_id'],
                'submission_form_ids': [sf.id for sf in value.pop('submission_forms', [])],
            }
            if 'extra' in value:
                v['extra'] = {
                    'old_submission_form_id': value['extra']['old_submission_form'].id,
                    'new_submission_form_id': value['extra']['new_submission_form'].id,
                }
            if 'form' in value:
                v['POST'] = value['form']['data']
            value = v
        elif data.stash.group == 'ecs.core.views.submissions.create_submission_form':
            v = {
                'POST': value['form']['data'],
                'initial': {'submission_form': value['form']['initial']},
            }
            for key in ('measure', 'routinemeasure', 'nontesteduseddrug',
                        'foreignparticipatingcenter', 'investigator',
                        'investigatoremployee'):
                assert(value['formsets'][key]['data'] == value['form']['data'])
                v['initial'][key] = value['formsets'][key]['initial']
            submission = value.get('submission')
            if submission:
                v['submission_id'] = submission.id
            notification_type = value.get('notification_type')
            if notification_type:
                v['notification_type_id'] = notification_type.id
            if 'document_pks' in value:
                v['document_pks'] = value['document_pks']
            value = v
        else:
            assert(False)

        # Make sure the data is json serializable
        assert(json.loads(json.dumps(value)) == value)

        data.value = PickledObject(base64.b64encode(zlib.compress(pickle.dumps(value))).decode())
        data.save(update_fields=['value'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge'),
        ('docstash', '0004_uuidfield'),
    ]

    operations = [
        migrations.RunPython(fix_2to3),
    ]
