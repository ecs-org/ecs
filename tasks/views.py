# -*- coding: utf-8 -*-
import random

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, QueryDict
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.utils.security import readonly
from ecs.users.utils import user_flag_required, sudo
from ecs.core.models import Submission
from ecs.tasks.models import Task, TaskType
from ecs.tasks.forms import ManageTaskForm, TaskListFilterForm
from ecs.tasks.signals import task_accepted, task_declined


@readonly()
@user_flag_required('is_internal')
def task_backlog(request, submission_pk=None, template='tasks/log.html'):
    with sudo():
        tasks = Task.objects.all()
        if submission_pk:
            submission = get_object_or_404(Submission, pk=submission_pk)
            tasks = tasks.for_submission(submission)
        tasks = list(tasks.order_by('created_at'))

    return render(request, template, {
        'tasks': tasks,
    })


@readonly()
def my_tasks(request, template='tasks/compact_list.html', submission_pk=None, ignore_task_types=True):
    usersettings = request.user.ecs_settings

    filterdict = request.POST or request.GET or None
    if filterdict is None and not usersettings.task_filter is None:
        filterdict = QueryDict(usersettings.task_filter)
    filterform = TaskListFilterForm(filterdict)
    filterform.is_valid() # force clean

    if request.method == 'POST':
        usersettings.task_filter = filterform.urlencode()
        usersettings.save()
        if len(request.GET.values()) > 0:
            return HttpResponseRedirect(request.path)

    sortings = {
        'deadline': 'workflow_token__deadline',
        'oldest': 'created_at',
        'newest': '-created_at',
    }
    sorting = 'deadline'
    if filterform.is_valid():
        sorting = filterform.cleaned_data['sorting'] or 'deadline'
    order_by = ['task_type__name', sortings[sorting], 'assigned_at']

    all_tasks = Task.objects.for_widget(request.user).filter(closed_at__isnull=True).select_related('task_type', 'task_type__workflow_node')

    submission = None
    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        tasks = all_tasks.for_submission(submission)
    elif not filterform.is_valid():
        tasks = all_tasks
    else:
        cd = filterform.cleaned_data
        past_meetings = cd['past_meetings']
        next_meeting = cd['next_meeting']
        upcoming_meetings = cd['upcoming_meetings']
        no_meeting = cd['no_meeting']
        amg = cd['amg']
        mpg = cd['mpg']
        thesis = cd['thesis']
        expedited = cd['expedited']
        local_ec = cd['local_ec']
        other = cd['other']

        if amg and mpg and thesis and expedited and local_ec and other and past_meetings and next_meeting and upcoming_meetings and no_meeting:
            tasks = all_tasks
        else:
            from ecs.votes.models import Vote
            submission_ct = ContentType.objects.get_for_model(Submission)
            vote_ct = ContentType.objects.get_for_model(Vote)
            submission_tasks = all_tasks.filter(content_type=submission_ct)
            vote_tasks = all_tasks.filter(content_type=vote_ct)
            tasks = all_tasks.exclude(content_type=submission_ct).exclude(content_type=vote_ct)

            if not (past_meetings and next_meeting and upcoming_meetings and no_meeting):
                qs = []
                if past_meetings:
                    qs += [Q(pk__in=Submission.objects.past_meetings().values('pk').query)]
                if next_meeting:
                    qs += [Q(pk__in=Submission.objects.next_meeting().values('pk').query)]
                if upcoming_meetings:
                    qs += [Q(pk__in=Submission.objects.upcoming_meetings().values('pk').query)]
                if no_meeting:
                    qs += [Q(pk__in=Submission.objects.no_meeting().values('pk').query)]
                if qs:
                    q = reduce(lambda x,y: x|y, qs)
                    submission_tasks = submission_tasks.filter(data_id__in=Submission.objects.filter(q).values('pk').query)
                    vote_tasks = vote_tasks.filter(data_id__in=Vote.objects.filter(submission_form__submission__pk__in=Submission.objects.filter(q).values('pk').query).values('pk').query)
                else:
                    submission_tasks = submission_tasks.none()
                    vote_tasks = vote_tasks.none()

            if not (amg and mpg and thesis and expedited and local_ec and other):
                amg_q = Q(pk__in=Submission.objects.amg().values('pk').query)
                mpg_q = Q(pk__in=Submission.objects.mpg().values('pk').query)
                retrospective_thesis_q = Q(pk__in=Submission.objects.for_thesis_lane().values('pk').query)
                expedited_q = Q(pk__in=Submission.objects.expedited())
                local_ec_q = Q(pk__in=Submission.objects.localec())
                qs = []
                if amg:
                    qs += [amg_q]
                if mpg:
                    qs += [mpg_q]
                if thesis:
                    qs += [retrospective_thesis_q]
                if expedited:
                    qs += [expedited_q]
                if local_ec:
                    qs += [local_ec_q]
                if other:
                    qs += [~amg_q & ~mpg_q & ~retrospective_thesis_q & ~expedited_q & ~local_ec_q]
                if qs:
                    q = reduce(lambda x,y: x|y, qs)
                    submission_tasks = submission_tasks.filter(data_id__in=Submission.objects.filter(q).values('pk').query)
                    vote_tasks = vote_tasks.filter(data_id__in=Vote.objects.filter(submission_form__submission__pk__in=Submission.objects.filter(q).values('pk').query).values('pk').query)
                else:
                    submission_tasks = submission_tasks.none()
                    vote_tasks = vote_tasks.none()

            tasks |= submission_tasks
            tasks |= vote_tasks
    
        if not ignore_task_types:
            task_types = filterform.cleaned_data['task_types']
            if task_types:
                tasks = tasks.filter(task_type__in=task_types)

    data = {
        'submission': submission,
        'filterform': filterform,
        'form_id': 'task_list_filter_%s' % random.randint(1000000, 9999999),
        'bookmarklink': '{0}?{1}'.format(request.build_absolute_uri(request.path), filterform.urlencode()),
    }

    task_flavors = {
        'mine': Q(assigned_to=request.user, accepted=True),
        'assigned': Q(assigned_to=request.user, accepted=False),
        'open': Q(assigned_to=None),
        'proxy': Q(assigned_to__ecs_profile__is_indisposed=True),
    }

    for k, q in task_flavors.iteritems():
        ck = '%s_tasks' % k
        on = not filterform.is_valid() or filterform.cleaned_data[k]
        data[ck] = tasks.filter(q).order_by(*order_by) if on else tasks.none()

    return render(request, template, data)


@readonly()
def task_list(request, **kwargs):
    kwargs.setdefault('template', 'tasks/list.html')
    kwargs.setdefault('ignore_task_types', False)
    return my_tasks(request, **kwargs)


@require_POST
def accept_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.acceptable_for_user(request.user), pk=task_pk)
    task.accept(request.user)
    task_accepted.send(type(task.node_controller), task=task)

    submission_pk = request.GET.get('submission')
    view = 'ecs.tasks.views.task_list' if full else 'ecs.tasks.views.my_tasks'
    return redirect_to_next_url(request, reverse(view, kwargs={'submission_pk': submission_pk} if submission_pk else None))

@require_POST
def accept_task_full(request, task_pk=None):
    return accept_task(request, task_pk=task_pk, full=True)

@require_POST
def accept_task_type(request, flavor=None, slug=None, full=False):
    tasks = Task.objects.for_widget(request.user).filter(closed_at__isnull=True)
    task_flavors = {
        'assigned': tasks.filter(assigned_to=request.user, accepted=False),
        'open': tasks.filter(assigned_to=None),
        'proxy': tasks.filter(assigned_to__ecs_profile__is_indisposed=True),
    }
    tasks = task_flavors[flavor]

    submission_pk = request.GET.get('submission')
    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)
        tasks = tasks.for_submission(submission)

    for task in tasks.acceptable_for_user(request.user).filter(task_type__workflow_node__uid=slug).order_by('created_at'):
        task.accept(request.user)
        task_accepted.send(type(task.node_controller), task=task)

    view = 'ecs.tasks.views.task_list' if full else 'ecs.tasks.views.my_tasks'
    return redirect_to_next_url(request, reverse(view, kwargs={'submission_pk': submission_pk} if submission_pk else None))

@require_POST
def accept_task_type_full(request, flavor=None, slug=None):
    return accept_task_type(request, flavor=flavor, slug=slug, full=True)

@require_POST
def decline_task(request, task_pk=None, full=False):
    task = get_object_or_404(Task.objects.filter(assigned_to=request.user), pk=task_pk)
    task.assign(None)
    task_declined.send(type(task.node_controller), task=task)

    submission_pk = request.GET.get('submission')
    view = 'ecs.tasks.views.task_list' if full else 'ecs.tasks.views.my_tasks'
    return redirect_to_next_url(request, reverse(view, kwargs={'submission_pk': submission_pk} if submission_pk else None))

@require_POST
def decline_task_full(request, task_pk=None):
    return decline_task(request, task_pk=task_pk, full=True)


def reopen_task(request, task_pk=None):
    task = get_object_or_404(Task, assigned_to=request.user, pk=task_pk)
    if task.workflow_token.workflow.is_finished:
        raise Http404()
    if not task.node_controller.is_repeatable():
        raise Http404()
    new_task = task.reopen(user=request.user)
    return HttpResponseRedirect(new_task.url)

def do_task(request, task_pk=None):
    task = get_object_or_404(Task, assigned_to=request.user, pk=task_pk)
    url = task.url
    if not task.closed_at is None:
        url = task.afterlife_url
        if url is None:
            raise Http404()
    return HttpResponseRedirect(url)
