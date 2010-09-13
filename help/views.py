from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from ecs.utils.viewutils import render

from ecs.tracking.models import View
from ecs.help.models import Page, Attachment
from ecs.help.forms import HelpPageForm


def redirect_to_page(page):
    return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))


def view_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    related_pages = Page.objects.filter(view=page.view).exclude(pk=page.pk).order_by('title')
    return render(request, 'help/view_page.html', {
        'page': page,
        'related_pages': related_pages,
    })


def delete_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    page.delete()
    return HttpResponseRedirect(reverse('ecs.help.views.index'))


def find_help(request, view_pk=None, anchor=''):
    pages = Page.objects.filter(view=int(view_pk))
    view = View.objects.get(pk=view_pk)

    if len(pages) == 1:
        return redirect_to_page(pages[0])
    elif len(pages) > 1:
        try:
            page = pages.get(anchor=anchor)
            return redirect_to_page(page)
        except Page.DoesNotExist:
            return render(request, 'help/index.html', {
                'view': view,
                'pages': pages,
            })
    return HttpResponseRedirect(reverse('ecs.help.views.index'))

def edit_help_page(request, view_pk=None, anchor='', page_pk=None):
    if page_pk:
        page = get_object_or_404(Page, pk=page_pk)
        view = page.view
    elif view_pk:
        view = get_object_or_404(View, pk=view_pk)
        try:
            page = Page.objects.get(view=view, anchor=anchor)
        except Page.DoesNotExist:
            page = None
    else:
        view = None
        page = None
    form = HelpPageForm(request.POST or None, instance=page, initial={'anchor': anchor, 'view': getattr(view, 'pk', None)})

    if form.is_valid():
        page = form.save()
        return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))
        
    related_pages = Page.objects.filter(view=view).order_by('title')
    if page:
        related_pages = related_pages.exclude(pk=page.pk)

    return render(request, 'help/edit_page.html', {
        'page': page,
        'view': view,
        'form': form,
        'related_pages': related_pages,
    })
    
def index(request):
    return render(request, 'help/index.html', {
        'pages': Page.objects.order_by('title'),
    })
    
def attachments(request):
    attachments = Attachment.objects.order_by('name')
    return render(request, 'help/attachments.html', {
        'attachments': attachments,
    })


def preview_help_page_text(request):
    text = request.POST.get('text', '')
    from django.contrib.markup.templatetags.markup import restructuredtext
    return HttpResponse(unicode(restructuredtext(text)))

