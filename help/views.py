import re
import tempfile
import datetime
from base64 import b64decode

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.core.files import File
from django.db.models import Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from reversion import revision

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.tracking.models import View
from ecs.users.utils import user_flag_required
from ecs.help.models import Page, Attachment
from ecs.help.forms import HelpPageForm, AttachmentUploadForm
from ecs.help.utils import publish_parts


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
        page = form.save()
        revision.user = request.original_user if hasattr(request, "original_user") else request.user
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


@user_flag_required('help_writer')
@revision.create_on_success
def delete_help_page(request, page_pk=None):
    page = get_object_or_404(Page, pk=page_pk)
    page.delete()
    revision.user = request.original_user if request.original_user else request.user
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
            slug = 'screenshot_%s.%s' % (datetime.datetime.now().strftime('%y%m%d%H%I%S'), mimetype[-3:])
        
        tmp = tempfile.NamedTemporaryFile() 
        tmp.write(data) 
        tmp.flush() 
        tmp.seek(0)
        Attachment.objects.create(file=File(tmp), mimetype=mimetype, screenshot=True, slug=slug)
        tmp.close() 

    return HttpResponse('OK')
