from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _

from reversion.models import Version

from ecs.checklists.models import ChecklistAnswer
from ecs.votes.models import Vote
from ecs.notifications.models import NotificationAnswer
from ecs.meetings.models import TimetableEntry
from ecs.core.diff import word_diff


ALLOWED_MODEL_FIELDS = {
    'checklist_answer': (ChecklistAnswer,
        (('answer', _('Answer')), ('comment', _('Comment')),)),
    'vote': (Vote, (('result', _('Vote')), ('text', _('Text')),)),
    'notification_answer': (NotificationAnswer, (('text', _('Text')),)),
    'timetable_entry': (TimetableEntry, (('text', _('Text')),)),
}


def _render_value(val):
    return {
        None: '',
        False: ugettext('No'),
        True: ugettext('Yes'),
    }.get(val, str(val))


def field_history(request, model_name=None, pk=None):
    try:
        model, fields = ALLOWED_MODEL_FIELDS[model_name]
    except KeyError:
        raise Http404()
    
    obj = get_object_or_404(model, pk=pk)

    if (model != ChecklistAnswer or request.user != obj.checklist.last_edited_by) and \
            not request.user.profile.is_internal:
        raise Http404()

    history = []
    last_value = {fieldname: '' for fieldname, label in fields}
    last_change = None
    versions = Version.objects.get_for_object(obj).order_by(
        'revision__date_created')
    for change in versions:
        diffs = []
        for fieldname, label in fields:
            value = _render_value(change.field_dict[fieldname])
            diffs += [(label, word_diff(last_value[fieldname], value))]
            last_value[fieldname] = value

        # Skip duplicate entries.
        if (last_change and
            last_change.revision.user == change.revision.user and
            all(len(d) == 1 and d[0][0] == 0 for l,d in diffs)):
            continue

        html_diffs = []
        for label, diff in diffs:
            html_diff = []
            for op, line in diff:
                line = line.replace('\n', '<br/>')
                if op:
                    html_diff.append('<span class="%s">%s</span>' % ('inserted' if op > 0 else 'deleted', line))
                else:
                    html_diff.append(line)
            if len(html_diff) == 1 and not html_diff[0]:
                html_diff = []
            html_diffs += [(label, ''.join(html_diff))]
        
        history.append({
            'timestamp': change.revision.date_created,
            'user': change.revision.user,
            'diffs': html_diffs,
        })
        last_change = change
    
    history.reverse()

    return render(request, 'field_history/diff.html', {
        'object': obj,
        'history': history,
    })
