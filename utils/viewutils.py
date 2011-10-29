from django.template import Context, RequestContext, loader, Template
from django.http import HttpResponse, HttpResponseRedirect
from piston.handler import BaseHandler

from ecs.utils.pdfutils import wkhtml2pdf

def render_html(request, template, context):
    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not isinstance(template, Template):
        template = loader.get_template(template)
    return template.render(RequestContext(request, context))

def render(request, template, context, mimetype=None):
    return HttpResponse(render_html(request, template, context), mimetype=mimetype)

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

def pdf_response(pdf, filename='Unnamed.pdf'):
    assert len(pdf) > 0
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename="%s"' % filename.replace('"', '_')
    return response

def render_pdf(request, template, context):
    html = render_html(request, template, context)
    footer_html = render_html(request, 'wkhtml2pdf/footer.html', context)
    return wkhtml2pdf(html, footer_html=footer_html)

def render_pdf_context(template, context):
    if not isinstance(template, Template):
        template = loader.get_template(template)
    html = template.render(Context(context))
    footer_template = loader.get_template('wkhtml2pdf/footer.html')
    footer_html = footer_template.render(Context(context))
    return wkhtml2pdf(html, footer_html=footer_html)
