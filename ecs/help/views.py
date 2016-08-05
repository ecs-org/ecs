import os
import re
import tempfile
import mimetypes
from base64 import b64decode

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.text import slugify

from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter

from reversion.models import Version
from reversion import revisions as reversion

from diff_match_patch import diff_match_patch

from ecs.utils.viewutils import redirect_to_next_url
from ecs.tracking.models import View
from ecs.users.utils import user_group_required
from ecs.help.models import Page, Attachment
from ecs.help.forms import HelpPageForm, AttachmentUploadForm, ImportForm
from ecs.help.utils import publish_parts
from ecs.help import serializer
from ecs.utils import forceauth


def redirect_to_page(page):
    return redirect('ecs.help.views.view_help_page', page_pk=page.pk)


@forceauth.exempt
def view_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    available_versions = Version.objects.get_for_object(page)
    return render(request, 'help/view_page.html', {
        'page': page,
        'versions': available_versions.count(),
        'current': available_versions.latest('revision__date_created'),
    })


@forceauth.exempt
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
    return redirect('ecs.help.views.index')


@forceauth.exempt
def index(request):
    try:
        page = Page.objects.get(slug='index')
        return redirect('ecs.help.views.view_help_page', page_pk=page.pk)
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


@forceauth.exempt
def download_attachment(request, attachment_pk=None):
    attachment = get_object_or_404(Attachment, pk=attachment_pk)
    return HttpResponse(attachment.content, content_type=attachment.mimetype)

@user_group_required('Help Writer')
def ready_for_review(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk, review_status__in=['new', 'review_ok', 'review_fail'])
    page.review_status = 'ready_for_review'
    page.save()
    # TODO: create trac testing ticket
    return redirect('ecs.help.views.view_help_page', page_pk=page.pk)

@user_group_required('Help Writer')
def review_ok(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk, review_status='ready_for_review')
    page.review_status = 'review_ok'
    page.save()
    return redirect('ecs.help.views.view_help_page', page_pk=page.pk)

@user_group_required('Help Writer')
def review_fail(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk, review_status='ready_for_review')
    page.review_status = 'review_fail'
    page.save()
    return redirect('ecs.help.views.view_help_page', page_pk=page.pk)

@user_group_required('Help Writer')
def review_overview(request):
    ready_for_review = Page.objects.filter(review_status='ready_for_review')
    review_fail = Page.objects.filter(review_status='review_fail')
    new = Page.objects.filter(review_status='new')
    review_ok = Page.objects.filter(review_status='review_ok')
    return render(request, 'help/review_overview.html', {
        'ready_for_review': ready_for_review,
        'review_fail': review_fail,
        'new': new,
        'review_ok': review_ok,
    })

@user_group_required('Help Writer')
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
        reversion.set_user(getattr(request, 'original_user', request.user))
        if new and page.slug:
            try:
                index = Page.objects.get(slug='index')
                index.text += "\n\n:doc:`%s <%s>`\n" % (page.title, page.slug)
                index.save()
            except Page.DoesNotExist:
                pass
        return redirect('ecs.help.views.view_help_page', page_pk=page.pk)

    return render(request, 'help/edit_page.html', {
        'page': page,
        'view': view,
        'form': form,
    })
    
    
HIGHLIGHT_PREFIX_WORD_COUNT = 3

class HelpHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        best_start, best_end = super().find_window(highlight_locations)
        return (max(0, best_start - 1 - len(' '.join(self.text_block[:best_start].rsplit(' ', HIGHLIGHT_PREFIX_WORD_COUNT + 1)[1:]))), best_end)


class HelpSearchView(SearchView):
    session_key = 'ecs.help.views.search:q'

    def get_query(self):
        q = super().get_query()
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


def search(request, *args, **kwargs):
    search_view = HelpSearchView(
        template='help/search.html',
        searchqueryset=SearchQuerySet().models(Page).order_by('title'),
        form_class=HighlightedSearchForm,
    )
    return search_view(request, *args, **kwargs)


@user_group_required('Help Writer')
def delete_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    page.delete()
    reversion.set_user(getattr(request, 'original_user', request.user))
    return redirect('ecs.help.views.index')


@user_group_required('Help Writer')
def preview_help_page_text(request):
    text = request.POST.get('text', '')
    return HttpResponse(publish_parts(text)['fragment'])
    

@user_group_required('Help Writer')
def difference_help_pages(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    try:
        new, old = Version.objects.get_for_object(page).order_by(
            '-revision__date_created')[:2]
    except ValueError:
        return HttpResponse("<html><body>no revisions</body></html>")

    dmp = diff_match_patch()
    diffs = dmp.diff_main(old.field_dict['text'], new.field_dict['text'])
    dmp.diff_cleanupSemantic(diffs)
    return HttpResponse(dmp.diff_prettyHtml(diffs))


@user_group_required('Help Writer')
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

        f = form.cleaned_data['file']
        attachment.content = f.read()
        attachment.mimetype = mimetypes.guess_type(f.name)[0]

        if not attachment.slug:
            name, ext = os.path.splitext(f.name)
            base_slug = slugify(name)
            slug = base_slug + ext
            i = 1
            while Attachment.objects.filter(slug=slug).exists():
                slug = '{}_{:02d}{}'.format(base_slug, i, ext)
                i += 1
            attachment.slug = slug

        attachment.save()
        return redirect_to_next_url(request, reverse('ecs.help.views.index'))
    return render(request, 'help/attachments/upload.html', {
        'form': form,
    })


@user_group_required('Help Writer')
def delete_attachment(request, attachment_pk):
    attachment = get_object_or_404(Attachment, pk=attachment_pk)
    attachment.delete()
    return HttpResponse('OK')


@user_group_required('Help Writer')
def find_attachments(request):
    return render(request, 'help/attachments/find.html', {
        'attachments': Attachment.objects.filter(slug__icontains=request.GET.get('q', '')).order_by('slug')[:5]
    })


#@user_group_required('Help Writer')
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
            slug = 'screenshot_%s.%s' % (timezone.now().strftime('%y%m%d%H%I%S'), mimetype[-3:])
        
        tmp = tempfile.NamedTemporaryFile() 
        tmp.write(data) 
        tmp.flush() 
        tmp.seek(0)
        Attachment.objects.create(file=File(tmp), mimetype=mimetype, is_screenshot=True, slug=slug)
        tmp.close() 

    return HttpResponse('OK')

@user_group_required('Help Writer')
def export(request):
    with tempfile.TemporaryFile(mode='w+b') as tmpfile:
        serializer.export(tmpfile)
        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), content_type='application/ech')
    response['Content-Disposition'] = 'attachment;filename=help-{0}.ech'.format(timezone.now().strftime('%Y-%m-%d'))
    return response

@user_group_required('Help Writer')
def load(request):
    form = ImportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        serializer.load(request.FILES['file'])
        form = ImportForm(None)

    return render(request, 'help/import.html', {
        'form': form,
    })


