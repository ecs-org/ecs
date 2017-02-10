from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db.models import Q, Prefetch
from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import redirect_to_next_url
from ecs.core.models import Submission
from ecs.communication.models import Thread, Message
from ecs.communication.forms import SendMessageForm, ReplyDelegateForm
from ecs.communication.forms import ThreadListFilterForm
from ecs.communication.utils import send_message
from ecs.users.utils import user_flag_required
from ecs.users.models import UserProfile


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


def star(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.star(request.user)
    return redirect_to_next_url(request, reverse('ecs.communication.views.dashboard_widget'))


def unstar(request, thread_pk=None):
    thread = get_object_or_404(Thread.objects.by_user(request.user), pk=thread_pk)
    thread.unstar(request.user)
    return redirect_to_next_url(request, reverse('ecs.communication.views.dashboard_widget'))


def dashboard_widget(request):
    qs = Thread.objects.for_widget(request.user).select_related(
        'last_message', 'last_message__sender', 'last_message__receiver',
        'submission',
    ).only(
        'starred_by_sender', 'starred_by_receiver',
        'subject', 'sender_id', 'receiver_id',

        'last_message__unread', 'last_message__timestamp',
        'last_message__sender_id', 'last_message__receiver_id',
        'last_message__text',

        'last_message__sender__first_name',
        'last_message__sender__last_name',
        'last_message__sender__email',

        'last_message__receiver__first_name',
        'last_message__receiver__last_name',
        'last_message__receiver__email',

        'submission__ec_number',
    ).prefetch_related(
        Prefetch('last_message__sender__profile',
            queryset=UserProfile.objects.only('gender', 'title', 'user_id')),
        Prefetch('last_message__receiver__profile',
            queryset=UserProfile.objects.only('gender', 'title', 'user_id')),
    ).order_by('-last_message__timestamp')

    try:
        page_num = int(request.GET.get('p', 1))
    except ValueError:
        page_num = 1

    paginator = Paginator(qs, 5)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)

    return render(request, 'communication/widget.html', {'page': page})


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


def list_threads(request, submission_pk=None):
    queryset = Thread.objects.by_user(request.user)

    filter_defaults = {'page': '1'}
    for key in ('incoming', 'outgoing', 'starred', 'unstarred'):
        filter_defaults[key] = 'on'

    if submission_pk:
        queryset = queryset.filter(submission_id=submission_pk)

        filterform = ThreadListFilterForm(request.POST or filter_defaults)
        filterform.is_valid() # force clean

        template = 'communication/threads_submission.html'
    else:
        usersettings = request.user.ecs_settings

        filterform = ThreadListFilterForm(
            request.POST or usersettings.communication_filter or filter_defaults)
        filterform.is_valid() # force clean

        usersettings.communication_filter = filterform.cleaned_data.copy()
        usersettings.communication_filter.pop('query', None)
        usersettings.save()

        template = 'communication/threads_full.html'

    filters = filterform.cleaned_data

    if filters['incoming'] and filters['outgoing']:
        pass
    elif filters['incoming']:
        queryset = queryset.exclude(last_message__sender=request.user)
    elif filters['outgoing']:
        queryset = queryset.filter(last_message__sender=request.user)
    else:
        queryset = queryset.none()

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

    if filters.get('query'):
        queryset = queryset.annotate(
            match=RawSQL("searchvector @@ plainto_tsquery('german', %s)",
                (filters['query'],))
        ).filter(match=True)

    queryset = queryset.select_related(
        'last_message', 'last_message__sender', 'last_message__receiver',
        'submission',
    ).only(
        'starred_by_sender', 'starred_by_receiver',
        'subject', 'sender_id', 'receiver_id',

        'last_message__unread', 'last_message__timestamp',
        'last_message__sender_id', 'last_message__receiver_id',
        'last_message__text',

        'last_message__sender__first_name',
        'last_message__sender__last_name',
        'last_message__sender__email',

        'last_message__receiver__first_name',
        'last_message__receiver__last_name',
        'last_message__receiver__email',

        'submission__ec_number',
    ).prefetch_related(
        Prefetch('last_message__sender__profile',
            queryset=UserProfile.objects.only('gender', 'title', 'user_id')),
        Prefetch('last_message__receiver__profile',
            queryset=UserProfile.objects.only('gender', 'title', 'user_id')),
    ).order_by('-last_message__timestamp')

    paginator = Paginator(queryset, 20)
    try:
        page = paginator.page(filters['page'] or 1)
    except EmptyPage:
        page_num = paginator.num_pages
        page = paginator.page(page_num)

    return render(request, template, {
        'page': page,
        'filterform': filterform,
        'submission_pk': submission_pk,
    })
