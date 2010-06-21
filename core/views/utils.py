from django.template import RequestContext, Context, loader, Template
from django.http import HttpResponse, HttpResponseRedirect
from piston.handler import BaseHandler

from ecs.utils.xhtml2pdf import xhtml2pdf

def render(request, template, context):
    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not isinstance(template, Template):
        template = loader.get_template(template)
    return HttpResponse(template.render(RequestContext(request, context)))

def redirect_to_next_url(request, default_url=None):
    next = request.REQUEST.get('next')
    if not next or '//' in next:
        next = default_url or '/'
    return HttpResponseRedirect(next)

class CsrfExemptBaseHandler(BaseHandler):
    def flatten_dict(self, dct):
        if 'csrfmiddlewaretoken' in dct:
            dct = dct.copy()
            del dct['csrfmiddlewaretoken']
        return super(CsrfExemptBaseHandler, self).flatten_dict(dct)

def render_pdf(request, template, context, filename='Unnamed.pdf'):
    html = render(request, template, context).content
    pdf = xhtml2pdf(html)
    assert len(pdf) > 0
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=%s' % filename
    return response


