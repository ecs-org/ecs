from django.utils.functional import wraps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from ecs.docstash.models import DocStash
from ecs.docstash.exceptions import ConcurrentModification, UnknownVersion

def with_docstash_transaction(*args, **kwargs):
    def decorator(view):
        view_name = "%s.%s" % (view.__module__, view.__name__)

        @wraps(view)
        def decorated(request, docstash_key=None, **kwargs):
            if not docstash_key:
                docstash = DocStash.objects.create(group=view_name, owner=request.user)
                kwargs['docstash_key'] = docstash.key
                response = HttpResponseRedirect(reverse(view_name, kwargs=kwargs))
            else:
                docstash = get_object_or_404(DocStash, group=view_name, owner=request.user, key=docstash_key)
                request.docstash = docstash
                # XXX: this is a simplification and only sufficient for our single-user application
                version = docstash.current_version 
                try:
                    docstash.start_transaction(version)
                except UnknownVersion, e:
                    raise Http404(str(e))
                try:
                    response = view(request, **kwargs)
                    try:
                        docstash.commit_transaction()
                    except ConcurrentModification:
                        # FIXME: handle concurrent updates (FMD1)
                        raise
                except:
                    docstash.rollback_transaction()
                    raise
            return response
        return decorated
    
    if args:
        return decorator(args[0])
    return decorator   