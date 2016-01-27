from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from ecs.utils.pdfutils import wkhtml2pdf

def render_html(request, template, context):
    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not hasattr(template, 'render'):
        template = loader.get_template(template)
    return template.render(context, request)

def redirect_to_next_url(request, default_url=None):
    next = request.GET.get('next')
    if not next or '//' in next:
        next = default_url or '/'
    return HttpResponseRedirect(next)

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
    if not hasattr(template, 'render'):
        template = loader.get_template(template)
    html = template.render(context)
    footer_template = loader.get_template('wkhtml2pdf/footer.html')
    footer_html = footer_template.render(context)
    return wkhtml2pdf(html, footer_html=footer_html)