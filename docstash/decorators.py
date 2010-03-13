from django.utils.functional import wraps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from ecs.docstash.models import DocStash
from ecs.docstash.exceptions import ConcurrentModification, UnknownVersion

VERSION_COOKIE_NAME = 'docstash_%s'

# FIXME: version cookies need to be signed
def with_docstash_transaction(view):
    view_name = "%s.%s" % (view.__module__, view.__name__)

    @wraps(view)
    def decorated(request, docstash_key=None, **kwargs):
        if not docstash_key:
            docstash = DocStash.objects.create(group=view_name)
            kwargs['docstash_key'] = docstash.key
            response = HttpResponseRedirect(reverse(view_name, kwargs=kwargs))
        else:
            docstash = get_object_or_404(DocStash, group=view_name, key=docstash_key)
            request.docstash = docstash
            version = request.COOKIES.get(VERSION_COOKIE_NAME % docstash.key, None)
            if version is None and request.method == 'GET':
                version = docstash.version
            else:
                version = int(version)
            try:
                docstash.start_transaction(version)
            except UnknownVersion, e:
                raise Http404(str(e))
            try:
                response = view(request, **kwargs)
                try:
                    docstash.commit_transaction()
                except ConcurrentModification:
                    # FIXME: handle concurrent updates
                    raise
            except:
                docstash.rollback_transaction()
                raise
            
        response.set_cookie(str(VERSION_COOKIE_NAME % docstash.key), str(docstash.current_version))
        return response
    return decorated