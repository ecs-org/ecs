# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import pickle
import struct
import zlib

from django.db import migrations, models


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

        value = pickle.loads(value, encoding='utf-8')

        # Make sure the transformation worked correctly.
        pickle.loads(pickle.dumps(value))

        data.value = PickledObject(base64.b64encode(zlib.compress(pickle.dumps(value))).decode())
        data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge'),
        ('docstash', '0004_uuidfield'),
    ]

    operations = [
        migrations.RunPython(fix_2to3),
    ]
