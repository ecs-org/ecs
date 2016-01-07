from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

from ecs.votes.models import Vote
from ecs.notifications.models import NotificationAnswer
from ecs.utils.security import readonly
from ecs.users.utils import user_flag_required
from ecs.core.diff import word_diff


ALLOWED_MODEL_FIELDS = {
    'vote': (Vote, (('result', _('Vote')), ('text', _('Text')),)),
    'notification_answer': (NotificationAnswer, (('text', _('Text')),)),
}


@readonly()
@user_flag_required('is_internal')
def field_history(request, model_name=None, pk=None):
    try:
        model, fields = ALLOWED_MODEL_FIELDS[model_name]
    except KeyError:
        raise Http404()
    
    obj = get_object_or_404(model, pk=pk)

    history = []
    last_value = dict((fieldname, '') for fieldname, label in fields)
    last_change = None
    versions = list(
        reversion.get_for_object(obj).order_by('revision__date_created')
    )
    for change in versions:
        diffs = []
        for fieldname, label in fields:
            value = change.field_dict[fieldname] or ''
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
