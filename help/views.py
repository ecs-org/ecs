import re
import tempfile
from datetime import datetime
from base64 import b64decode

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.core.files import File
from django.db.models import Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter

from reversion import revision

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.tracking.models import View
from ecs.users.utils import user_flag_required
from ecs.help.models import Page, Attachment
from ecs.help.forms import HelpPageForm, AttachmentUploadForm, ImportForm
from ecs.help.utils import publish_parts
from ecs.help import serializer
from ecs.utils.tracrpc import TracRpc


def redirect_to_page(page):
    return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))


def view_help_page(request, page_pk=None):
    from reversion.models import Version
    page = get_object_or_404(Page, pk=page_pk)
    related_pages = Page.objects.filter(view=page.view).exclude(pk=page.pk).order_by('title')
    available_versions = Version.objects.get_for_object(page)
    return render(request, 'help/view_page.html', {
        'page': page,
        'related_pages': related_pages,
        'versions': len(available_versions),
        'current': available_versions[len(available_versions)-1]
    })


def find_help(request, view_pk=None, anchor=''):
    anchor = request.GET.get('anchor', anchor)
    pages = Page.objects.filter(view=view_pk)
    if len(pages) == 1:
        return redirect_to_page(pages[0])
    elif len(pages) > 1:
        try:
            page = pages.get(anchor=anchor)
            return redirect_to_page(page)
        except Page.DoesNotExist:
            view = View.objects.get(pk=view_pk)
            return render(request, 'help/index.html', {
                'view': view,
                'anchor': anchor,
                'pages': pages,
            })
    return HttpResponseRedirect(reverse('ecs.help.views.index'))


def index(request):
    try:
        page = Page.objects.get(slug='index')
        return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))
    except Page.DoesNotExist:
        pass
    return render(request, 'help/index.html', {
        'pages': Page.objects.order_by('title'),
    })


def attachments(request):
    attachments = Attachment.objects.order_by('name')
    return render(request, 'help/attachments.html', {
        'attachments': attachments,
    })


def download_attachment(request, attachment_pk=None):
    attachment = get_object_or_404(Attachment, pk=attachment_pk)
    return HttpResponse(attachment.file.read(), content_type=attachment.mimetype)

@user_flag_required('help_writer')
def ready_for_review(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk, review_status__in=['new', 'review_ok'])
    page.review_status = 'ready_for_review'
    page.save()
    # TODO: create trac testing ticket
    return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))

@user_flag_required('help_writer')
def review_ok(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk, review_status='ready_for_review')
    page.review_status = 'review_ok'
    page.save()
    return HttpResponseRedirect(reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))

@user_flag_required('help_writer')
def review_overview(request):
    ready_for_review = Page.objects.filter(review_status='ready_for_review')
    new = Page.objects.filter(review_status='new')
    return render(request, 'help/review_overview.html', {
        'ready_for_review': ready_for_review,
        'new': new,
    })

@user_flag_required('help_writer')
@revision.create_on_success
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
    initial = {'view': getattr(view, 'pk', None)}
    if anchor:
        initial['anchor'] = request.GET.get('anchor', anchor)
    form = HelpPageForm(request.POST or None, instance=page, initial=initial)

    if form.is_valid():
        new = not bool(page)
        page = form.save()
        revision.user = request.original_user if hasattr(request, "original_user") else request.user
        if new and page.slug:
            try:
                index = Page.objects.get(slug='index')
                index.text += "\n\n:doc:`%s <%s>`\n" % (page.title, page.slug)
                index.save()
            except Page.DoesNotExist:
                pass
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
    
    
HIGHLIGHT_PREFIX_WORD_COUNT = 3

class HelpHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        best_start, best_end = super(HelpHighlighter, self).find_window(highlight_locations)
        return (max(0, best_start - 1 - len(' '.join(self.text_block[:best_start].rsplit(' ', HIGHLIGHT_PREFIX_WORD_COUNT + 1)[1:]))), best_end)


class HelpSearchView(SearchView):
    session_key = 'ecs.help.views.search:q'

    def get_query(self):
        q = super(HelpSearchView, self).get_query()
        self.request.session[self.session_key] = q
        return q

    def build_form(self, form_kwargs=None): # mostly copied from haystack.forms
        data = None
        kwargs = {
            'load_all': self.load_all,
        }
        if form_kwargs:
            kwargs.update(form_kwargs)

        q = self.request.session.get(self.session_key, '')

        if len(self.request.GET):
            data = self.request.GET

        if q and not data:
            data = {'q': q}

        if self.searchqueryset is not None:
            kwargs['searchqueryset'] = self.searchqueryset

        return self.form_class(data, **kwargs)


# haystack's search_view_factory does not pass *args and **kwargs
def search_view_factory(view_class=SearchView, *args, **kwargs):
    def search_view(request, *view_args, **view_kwargs):
        return view_class(*args, **kwargs)(request, *view_args, **view_kwargs)
    return search_view

search = search_view_factory(
    view_class=HelpSearchView,
    template='help/search.html',
    searchqueryset=SearchQuerySet().models(Page).order_by('title'),
    form_class=HighlightedSearchForm,
)



@user_flag_required('help_writer')
@revision.create_on_success
def delete_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    page.delete()
    revision.user = request.original_user if hasattr(request, "original_user") else request.user
    return HttpResponseRedirect(reverse('ecs.help.views.index'))


@user_flag_required('help_writer')
def preview_help_page_text(request):
    text = request.POST.get('text', '')
    return HttpResponse(publish_parts(text)['fragment'])
    

@user_flag_required('help_writer')
def difference_help_pages(request, page_pk=None, old_version="-2", new_version="-1"):
    from reversion.helpers import generate_patch_html
    from reversion.models import Version

    page = get_object_or_404(Page, pk=page_pk)
    available_versions = Version.objects.get_for_object(page)
    if len(available_versions) < 2:
        return HttpResponse("<html><body>no revisions</body></html>")

    old_version = int(old_version)
    new_version = int(new_version)
    if new_version < 0:
        new_version = len(available_versions)+ new_version
    if old_version < 0:
        old_version = len(available_versions)+ old_version

    new_content = available_versions[new_version]
    old_content = available_versions[old_version]
    return HttpResponse(generate_patch_html(old_content, new_content, "text"))


@user_flag_required('help_writer')
def upload(request):
    page, view = None, None
    if 'page' in request.GET:
        page = get_object_or_404(Page, pk=request.GET['page'])
    if 'view' in request.GET:
        view = get_object_or_404(View, pk=request.GET['view'])
    form = AttachmentUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        attachment = form.save(commit=False)
        attachment.page = page
        attachment.view = view
        attachment.save()
        return redirect_to_next_url(request, reverse('ecs.help.views.index'))
    return render(request, 'help/attachments/upload.html', {
        'form': form,
    })


@user_flag_required('help_writer')
def delete_attachment(request):
    attachment = get_object_or_404(Attachment, pk=request.POST.get('pk', None))
    attachment.delete()
    return HttpResponse('OK')


@user_flag_required('help_writer')
def find_attachments(request):
    return render(request, 'help/attachments/find.html', {
        'attachments': Attachment.objects.filter(slug__icontains=request.GET.get('q', '')).order_by('slug')[:5]
    })


#@user_flag_required('help_writer')
@csrf_exempt
def screenshot(request):
    dataurl = request.POST.get('image', None)
    if dataurl:
        head, data = dataurl.split(',', 1)
        match = re.match('data:(image/png|jpg);base64', head)
        if not match:
            return HttpResponseBadRequest("invalid data url: only base64 encoded image/png and image/jpg data will be accepted")
        mimetype = match.group(1)
        try:
            data = b64decode(data)
        except TypeError:
            return HttpResponseBadRequest("invalid base64 data")
        
        slug = request.POST.get('slug', '')
        if not slug:
            slug = 'screenshot_%s.%s' % (datetime.now().strftime('%y%m%d%H%I%S'), mimetype[-3:])
        
        tmp = tempfile.NamedTemporaryFile() 
        tmp.write(data) 
        tmp.flush() 
        tmp.seek(0)
        Attachment.objects.create(file=File(tmp), mimetype=mimetype, screenshot=True, slug=slug)
        tmp.close() 

    return HttpResponse('OK')

@user_flag_required('help_writer')
def export(request):
    with tempfile.TemporaryFile(mode='w+b') as tmpfile:
        serializer.export(tmpfile)
        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), mimetype='application/ech')
    response['Content-Disposition'] = 'attachment;filename=help-{0}.ech'.format(datetime.now().strftime('%Y-%m-%d'))
    return response

@user_flag_required('help_writer')
def load(request):
    form = ImportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        serializer.load(request.FILES['file'])
        form = ImportForm(None)

    return render(request, 'help/import.html', {
        'form': form,
    })


