from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import redirect_to_next_url
from ecs.core.models import Submission
from ecs.communication.models import Thread
from ecs.communication.forms import SendMessageForm, ReplyDelegateForm
from ecs.tracking.decorators import tracking_hint
from ecs.communication.forms import ThreadListFilterForm
from ecs.communication.utils import send_message
from ecs.users.utils import user_flag_required


def new_thread(request, submission_pk=None, to_user_pk=None):
    submission, to_user = None, None

    if submission_pk is not None:
        submission = get_object_or_404(Submission, pk=submission_pk)
    
    if to_user_pk is not None:
        to_user = get_object_or_404(User, pk=to_user_pk)

    form = SendMessageForm(submission, request.POST or None, to=to_user)
    thread = None

    if request.method == 'POST' and form.is_valid():
        thread = send_message(request.user, form.cleaned_data['receiver'], form.cleaned_data['subject'], form.cleaned_data['text'], submission=submission)
        return redirect_to_next_url(request, reverse('ecs.communication.views.read_thread', kwargs={'thread_pk': thread.pk}))

    return render(request, 'communication/send.html', {
        'submission': submission,
        'to_user': to_user,
        'form': form,
        'thread': thread,
    })


def read_thread(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.messages.filter(receiver=request.user).update(unread=False)

    form = ReplyDelegateForm(request.user, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        delegate_to = form.cleaned_data.get('to')
        # delegation is optional; if there is no delegation target, we just
        # append the message to the present thread, else we delegate the
        # present thread and create a new one with the message inside
        if delegate_to:
            thread.delegate(request.user, delegate_to)
            new_subject = format(thread.subject)
            if not new_subject.startswith('Bzgl.:'):
                new_subject =_('Bzgl.: {0}').format(thread.subject)[:100]
            thread = Thread.objects.create(
                subject=new_subject,
                sender=request.user,
                receiver=delegate_to,
                submission=thread.submission,
                related_thread=thread,
            )
        thread.add_message(request.user, form.cleaned_data['text'])
        form = ReplyDelegateForm(request.user, None)

    return render(request, 'communication/thread.html', {
        'thread': thread,
        'form': form,
    })


def mark_read(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.messages.filter(receiver=request.user).update(unread=False)
    return redirect_to_next_url(request,
        reverse('ecs.communication.views.dashboard_widget'))


@tracking_hint(exclude=True)
def star(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.star(request.user)
    return redirect_to_next_url(request, reverse('ecs.communication.views.dashboard_widget'))


@tracking_hint(exclude=True)
def unstar(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.unstar(request.user)
    return redirect_to_next_url(request, reverse('ecs.communication.views.dashboard_widget'))


@tracking_hint(exclude=True)
def dashboard_widget(request, submission_pk=None):
    qs = Thread.objects.for_widget(request.user).select_related(
        'last_message', 'last_message__sender', 'last_message__receiver',
        'last_message__sender__profile', 'last_message__receiver__profile',
        'submission',
    ).order_by('-last_message__timestamp')
    submission = None
    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        qs = qs.filter(submission=submission)

    try:
        page_num = int(request.GET.get('p', 1))
    except ValueError:
        page_num = 1

    paginator = Paginator(qs, 4)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)

    context = {
        'page': page,
        'submission': submission,
    }
    return render(request, 'communication/widget.html', context)


@tracking_hint(exclude=True)
@user_flag_required('is_internal')
def communication_overview_widget(request, submission_pk=None):
    threads = Thread.objects.filter(submission__pk=submission_pk)
    show_system_messages = bool(request.GET.get('show_system_messages'))
    if not show_system_messages:
        threads = threads.exclude(last_message__sender__email='root@system.local')

    return render(request, 'communication/overview.html', {
        'threads': threads.order_by('-last_message__timestamp'),
        'show_system_messages': show_system_messages,
    })


def message_widget(request, queryset=None, template=None, user_sort=None, session_prefix='messages', extra_context=None, page_size=4, submission=None):
    sort_session_key = '%s:sort' % session_prefix
    raw_sort = request.GET.get('sort', request.session.get(sort_session_key, '-last_message__timestamp'))
    
    sort_options = ('last_message__timestamp', 'user', 'submission')
    sort = raw_sort
    if sort:
        field = sort if sort[0] != '-' else sort[1:]
        if field not in sort_options:
            sort = None
        elif field == 'user':
            sort = sort.replace('user', user_sort) if user_sort else None
    if sort:
        queryset = queryset.order_by(sort)
    request.session[sort_session_key] = sort

    page_session_key = 'dashboard:%s:page' % session_prefix
    try:
        page_num = int(request.GET.get('p', request.session.get(page_session_key, 1)))
    except ValueError:
        page_num = 1

    queryset = queryset.select_related('last_message', 'last_message__sender', 'last_message__receiver',
        'last_message__sender__profile', 'last_message__receiver__profile', 'submission')
    paginator = Paginator(queryset, page_size)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)
    request.session[page_session_key] = page_num

    context = {
        'page': page,
        'sort': raw_sort,
        'submission': submission,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def list_threads(request):
    usersettings = request.user.ecs_settings

    filter_defaults = {}
    for key in ('incoming', 'outgoing', 'starred', 'unstarred'):
        filter_defaults[key] = 'on'

    filterform = ThreadListFilterForm(
        request.POST or usersettings.communication_filter or filter_defaults)
    filterform.is_valid() # force clean

    filters = usersettings.communication_filter = filterform.cleaned_data
    usersettings.save()

    if filters['incoming'] and filters['outgoing']:
        queryset = Thread.objects.by_user(request.user)
    elif filters['incoming']:
        queryset = Thread.objects.incoming(request.user)
    elif filters['outgoing']:
        queryset = Thread.objects.outgoing(request.user)
    else:
        queryset = Thread.objects.none()

    if filters['starred'] and filters['unstarred']:
        pass
    elif filters['starred']:
        queryset = queryset.filter(
            Q(starred_by_receiver=True, receiver=request.user) |
            Q(starred_by_sender=True, sender=request.user)
        )
    elif filters['unstarred']:
        queryset = queryset.filter(
            Q(starred_by_receiver=False, receiver=request.user) |
            Q(starred_by_sender=False, sender=request.user)
        )
    else:
        queryset = queryset.none()

    return message_widget(request, 
        template='communication/threads.html',
        queryset=queryset,
        session_prefix='messages:unified',
        user_sort='receiver__username',
        page_size=15,
        extra_context={'filterform': filterform},
    )
