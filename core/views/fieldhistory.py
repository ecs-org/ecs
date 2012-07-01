from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from ecs.votes.models import Vote
from ecs.notifications.models import NotificationAnswer
from ecs.utils.viewutils import render
from ecs.utils.security import readonly
from ecs.audit.utils import get_versions
from ecs.users.utils import sudo
from ecs.core.diff import word_diff


ALLOWED_MODEL_FIELDS = {
    'vote': (Vote, (('result', _('Vote')), ('text', _('Text')),)),
    'notification_answer': (NotificationAnswer, (('text', _('Text')),)),
}


@readonly()
def field_history(request, model_name=None, pk=None):
    try:
        model, fields = ALLOWED_MODEL_FIELDS[model_name]
    except KeyError:
        raise Http404()
    
    obj = get_object_or_404(model, pk=pk)

    history = []
    last_value = {}
    last_change = None
    for fieldname, label in fields:
        last_value[fieldname] = u''
    last_change = None
    i = 0
    with sudo():
        versions = list(get_versions(obj).order_by('created_at'))
    for change in versions:
        diffs = []
        for fieldname, label in fields:
            value = simplejson.loads(change.data)[0]['fields'][fieldname]
            diffs += [(label, word_diff(last_value[fieldname], value))]
            last_value[fieldname] = value
        if last_change and last_change.user == change.user and all(len(d) == 1 and d[0][0] == 0 for l,d in diffs):
            continue
        html_diffs = []
        for label, diff in diffs:
            html_diff = []
            for op, line in diff:
                line = line.replace('\n', '<br/>')
                if op:
                    html_diff.append(u'<span class="%s">%s</span>' % ('inserted' if op > 0 else 'deleted', line))
                else:
                    html_diff.append(line)
            if len(html_diff) == 1 and not html_diff[0]:
                html_diff = []
            html_diffs += [(label, u''.join(html_diff))]
        
        i += 1
        
        history.append({
            'timestamp': change.created_at,
            'user': change.user,
            'value': value,
            'diffs': html_diffs,
            'version_number': i,
        })
        last_change = change
    
    history.reverse()

    return render(request, 'field_history/diff.html', {
        'object': obj,
        'history': history,
    })
