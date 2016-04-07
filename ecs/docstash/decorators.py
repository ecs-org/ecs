from django.utils.functional import wraps
from django.shortcuts import redirect, get_object_or_404

from ecs.docstash.models import DocStash


def with_docstash(group=None):
    def _decorator(view):
        view_name = group or '.'.join((view.__module__, view.__name__))

        @wraps(view)
        def _inner(request, docstash_key=None, **kwargs):
            if not docstash_key:
                docstash = DocStash.objects.create(group=view_name, owner=request.user)
                return redirect(view_name, docstash_key=docstash.key, **kwargs)

            docstash = get_object_or_404(DocStash, group=view_name,
                owner=request.user, key=docstash_key)
            request.docstash = docstash
            return view(request, **kwargs)

        return _inner

    return _decorator
