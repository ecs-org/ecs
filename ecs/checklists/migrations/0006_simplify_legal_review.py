# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Q


def simplify_legal_review(apps, schema_editor):
    ChecklistBlueprint = apps.get_model('checklists', 'ChecklistBlueprint')
    try:
        blueprint = ChecklistBlueprint.objects.get(slug='legal_review')
    except ChecklistBlueprint.DoesNotExist:
        return

    for checklist in blueprint.checklists.all():
        non_empty = checklist.answers.exclude(
            Q(comment=None) | Q(comment=''), answer=None)
        if not non_empty.exists():
            continue

        if checklist.answers.filter(answer=None).exists():
            answer = None
        else:
            answer = not checklist.answers.filter(answer=False).exists()

        comment = []
        for a in checklist.answers.order_by('question__index'):
            comment.append('> {}. {}: {}\n{}'.format(a.question.number,
                a.question.text,
                {None: '-', True: 'Ja', False: 'Nein'}[a.answer],
                a.comment))

        checklist.answers.filter(question__number='1').update(
            answer=answer, comment='\n\n'.join(comment))

    blueprint.questions.filter(number='1').update(text=
        'Entspricht die Patienteninformation in allen Punkten den Anforderungen?')
    blueprint.questions.exclude(number='1').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0005_fix_external_review'),
    ]

    operations = [
        migrations.RunPython(simplify_legal_review),
    ]
