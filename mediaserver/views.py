# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext as _

from ecs.utils import forceauth
from ecs.utils.viewutils import render_html
from ecs.mediaserver.utils import MediaProvider, AuthUrl
        

@forceauth.exempt
def get_pdf(request, uuid, filename, branding):
    return get_blob(request, uuid, filename, mimetype='application/pdf', branding=branding)


@forceauth.exempt
def get_blob(request, uuid, filename, mimetype='application/pdf', branding=None):
    authurl = AuthUrl(settings.MS_CLIENT['key_id'], settings.MS_CLIENT['key_secret'])
    
    if not authurl.verify(request.get_full_path()):
        return HttpResponseBadRequest(_("Invalid expiring url"))

    f = None
    mediaprovider = MediaProvider()
    try:    
        try:
            if branding is not None:
                f = mediaprovider.get_branded(uuid, mimetype, True)
            else:
                f = mediaprovider.get_blob(uuid)
        except KeyError:
            html = render_html(request, 'mediaserver/202.html', {})
            return HttpResponse(html, status=202) # accepted, content not ready
            
        response = HttpResponse(f.read(), mimetype=mimetype)
        response['Content-Disposition'] = 'attachment;filename=%s' % (filename)
    finally:
        if hasattr(f, "close"):
            f.close()
    
    return response

