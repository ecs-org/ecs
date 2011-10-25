from diff_match_patch import diff_match_patch

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from ecs.votes.models import Vote
from ecs.notifications.models import NotificationAnswer
from ecs.utils.viewutils import render
from ecs.audit.utils import get_versions


ALLOWED_MODEL_FIELDS = {
    'vote': (Vote, 'text'),
    'notification_answer': (NotificationAnswer, 'text'),
}


def field_history(request, model_name=None, pk=None):
    try:
        model, fieldname = ALLOWED_MODEL_FIELDS[model_name]
    except KeyError:
        raise Http404()
    
    obj = get_object_or_404(model, pk=pk)
    dmp = diff_match_patch()

    history = []
    last_value = u""
    i = 0
    for change in get_versions(obj).order_by('created_at'):
        i += 1
        value = simplejson.loads(change.data)[0]['fields'][fieldname]
        diff = dmp.diff_main(last_value, value)
        dmp.diff_cleanupSemantic(diff)
        html_diff = []
        for op, line in diff:
            line = line.replace('\n', '<br/>')
            if op:
                html_diff.append(u'<span class="%s">%s</span>' % ('inserted' if op > 0 else 'deleted', line))
            else:
                html_diff.append(line)
        if len(html_diff) == 1 and not html_diff[0]:
            html_diff = []
        
        
        history.append({
            'timestamp': change.created_at,
            'user': change.user,
            'value': value,
            'diff': u''.join(html_diff),
            'version_number': i,
        })
        last_value = value
    
    history.reverse()

    return render(request, 'field_history/diff.html', {
        'object': obj,
        'history': history,
    })
