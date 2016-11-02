from datetime import datetime, timedelta
import random
from collections import defaultdict

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core import signing
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage

from ecs.utils import forceauth
from ecs.utils.viewutils import render_html
from ecs.utils.ratelimitcache import ratelimit_post
from ecs.communication.mailutils import deliver
from ecs.users.forms import RegistrationForm, ActivationForm, RequestPasswordResetForm, ProfileForm, AdministrationFilterForm, \
    UserDetailsForm, InvitationForm
from ecs.users.models import UserProfile, Invitation, LoginHistory
from ecs.users.forms import EmailLoginForm, IndispositionForm, SetPasswordForm, PasswordChangeForm, LoginHistoryFilterForm
from ecs.users.utils import get_user, create_user, user_flag_required, user_group_required
from ecs.communication.utils import send_message, send_system_message_template
from ecs.utils.browserutils import UA


class TimestampedTokenFactory(object):
    def __init__(self, key, salt, ttl=3600):
        self.key = key
        self.salt = salt
        self.ttl = ttl
        
    def generate_token(self, data):
        return signing.dumps(data, key=self.key, salt=self.salt)
        
    def parse_token(self, token):
        return signing.loads(token, key=self.key, salt=self.salt,
            max_age=self.ttl)

_password_reset_token_factory = TimestampedTokenFactory(
    settings.PASSWORD_RESET_SECRET, 'ecs.users.password_reset')
_registration_token_factory = TimestampedTokenFactory(
    settings.REGISTRATION_SECRET, 'ecs.users.registration', ttl=86400)

@forceauth.exempt
@ratelimit_post(minutes=5, requests=15, key_field='username')
def login(request, *args, **kwargs):
    if request.is_ajax():
        return HttpResponse('<script type="text/javascript">window.location.href="%s";</script>' % reverse('ecs.users.views.login'))

    ua_str = request.META.get('HTTP_USER_AGENT')
    if ua_str:
        request.ua = UA(ua_str)
        if request.ua.is_unsupported:
            return redirect(staticfiles_storage.url('help/html5.html'))
        elif request.ua.is_tmp_unsupported:
            return render(request, 'browser_temporarily_unsupported.html', {})

    kwargs.setdefault('template_name', 'users/login.html')
    kwargs['authentication_form'] = EmailLoginForm
    response = auth_views.login(request, *args, **kwargs)
    if request.user.is_authenticated():
        LoginHistory.objects.create(type='login', user=request.user,
            ip=request.META['REMOTE_ADDR'])

        profile = request.user.profile
        old_session_key = profile.session_key
        profile.session_key = request.session.session_key
        profile.save()

        Session.objects.filter(session_key=old_session_key).update(expire_date=timezone.now())

    return response


def logout(request, *args, **kwargs):
    kwargs.setdefault('next_page', '/')
    user_id = getattr(request, 'original_user', request.user).id
    response = auth_views.logout(request, *args, **kwargs)
    if not request.user.is_authenticated():
        LoginHistory.objects.create(type='logout', user_id=user_id,
            ip=request.META['REMOTE_ADDR'])
    return response


def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        UserProfile.objects.filter(user=request.user).update(last_password_change=timezone.now())
        return render(request, 'users/change_password_complete.html', {})
    return render(request, 'users/change_password_form.html', {
        'form': form,
    })


@forceauth.exempt
@ratelimit_post(minutes=5, requests=15, key_field='email')
def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        token = _registration_token_factory.generate_token(form.cleaned_data)
        activation_url = request.build_absolute_uri(reverse('ecs.users.views.activate', kwargs={'token': token}))        
        htmlmail = str(render_html(request, 'users/registration/activation_email.html', {
            'activation_url': activation_url,
            'form': form,
        }))
        deliver(form.cleaned_data['email'], subject=_('ECS - Registration'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL, nofilter=True)
        return render(request, 'users/registration/registration_complete.html', {})
        
    return render(request, 'users/registration/registration_form.html', {
        'form': form,
    })


@forceauth.exempt
def activate(request, token=None):
    try:
        data = _registration_token_factory.parse_token(token)
    except (signing.BadSignature, signing.SignatureExpired):
        return render(request, 'users/registration/registration_token_invalid.html', {})

    try:
        existing_user = get_user(data['email'])
        return render(request, 'users/registration/already_activated.html', {
            'existing_user': existing_user,
        })
    except User.DoesNotExist:
        pass

    form = ActivationForm(request.POST or None)
    if form.is_valid():
        user = create_user(data['email'], first_name=data['first_name'], last_name=data['last_name'])
        user.set_password(form.cleaned_data['password'])
        user.save()
        # the userprofile is auto-created, we only have to update some fields.
        profile = user.profile
        profile.gender = data['gender']
        profile.forward_messages_after_minutes = 5
        profile.save()

        return render(request, 'users/registration/activation_complete.html', {
            'activated_user': user,
        })
        
    return render(request, 'users/registration/activation_form.html', {
        'form': form,
        'data': data,
    })


@forceauth.exempt
@ratelimit_post(minutes=5, requests=15, key_field='email')
def request_password_reset(request):
    form = RequestPasswordResetForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        if email != 'root@system.local':
            try:
                user = get_user(email)
            except User.DoesNotExist:
                register_url = request.build_absolute_uri(reverse('ecs.users.views.register'))
                htmlmail = str(render_html(request, 'users/password_reset/register_email.html', {
                    'register_url': register_url,
                    'email': email,
                }))
            else:
                timestamp = (datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()
                token = _password_reset_token_factory.generate_token([email, timestamp])
                reset_url = request.build_absolute_uri(reverse('ecs.users.views.do_password_reset', kwargs={'token': token}))
                htmlmail = str(render_html(request, 'users/password_reset/reset_email.html', {
                    'reset_url': reset_url,
                }))
            deliver(email, subject=_('ECS - Password Reset'), message=None, message_html=htmlmail,
                from_email= settings.DEFAULT_FROM_EMAIL, nofilter=True)
        return render(request, 'users/password_reset/request_complete.html', {
            'email': email,
        })
    return render(request, 'users/password_reset/request_form.html', {
        'form': form,
    })


@forceauth.exempt
def do_password_reset(request, token=None):
    try:
        email, timestamp = _password_reset_token_factory.parse_token(token)
    except (signing.BadSignature, signing.SignatureExpired):
        return render(request, 'users/password_reset/reset_token_invalid.html', {})

    try:
        user = get_user(email)
    except User.DoesNotExist:
        raise Http404()
    profile = user.profile
    timestamp = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
    if profile.last_password_change and profile.last_password_change > timestamp:
        return render(request, 'users/password_reset/token_already_used.html', {})
    
    form = SetPasswordForm(user, request.POST or None)
    if form.is_valid():
        form.save()
        profile.last_password_change = timezone.now()
        profile.save()
        return render(request, 'users/password_reset/reset_complete.html', {})
    return render(request, 'users/password_reset/reset_form.html', {
        'user': user,
        'form': form,
    })


def profile(request):
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
    })

def edit_profile(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    
    if form.is_valid():
        form.save()
        return redirect('ecs.users.views.profile')
        
    return render(request, 'users/profile_form.html', {
        'form': form,
    })


###########################
### User Administration ###
###########################

def notify_return(request):
    profile = request.user.profile
    profile.is_indisposed = False
    profile.save()
    return redirect('ecs.users.views.profile')


@user_group_required('EC-Office', 'EC-Executive Board Member')
def indisposition(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    form = IndispositionForm(request.POST or None, instance=user.profile)

    if request.method == 'POST' and form.is_valid():
        form.save()
        profile = user.profile
        if profile.is_indisposed:
            send_system_message_template(profile.communication_proxy, _('{user} indisposed').format(user=user), 'users/indisposed_proxy.txt', {'user': user})
        return redirect('ecs.users.views.administration')

    return render(request, 'users/indisposition.html', {
        'profile_user': user,
        'form': form,
    })


@require_POST
@user_group_required('EC-Office', 'EC-Executive Board Member')
def toggle_active(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect('ecs.users.views.administration')


@user_group_required('EC-Office', 'EC-Executive Board Member')
def details(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    form = UserDetailsForm(request.POST or None, instance=user, prefix='user')
    if request.method == 'POST' and form.is_valid():
        was_signing_user = user.groups.filter(name='EC-Signing').exists()
        old_task_uids = set(user.profile.task_uids)

        user = form.save()

        new_task_uids = set(user.profile.task_uids)
        if old_task_uids != new_task_uids:
            msgs = defaultdict(lambda: {'added': [], 'removed': []})
            changed_task_types = form.fields['task_types'].queryset.filter(
                workflow_node__uid__in=
                    old_task_uids.symmetric_difference(new_task_uids)
            )
            for task_type in changed_task_types:
                if task_type.workflow_node.uid in new_task_uids:
                    what = 'added'
                else:
                    what = 'removed'
                for u in task_type.group.user_set.filter(is_active=True):
                    msgs[u][what].append(task_type)

            for recipient, changes in msgs.items():
                send_system_message_template(recipient,
                    _('Division of work with {user}').format(user=user),
                    'users/division_of_work.txt', {
                        'user': user,
                        'added': changes['added'],
                        'removed': changes['removed'],
                    })

        is_signing_user = user.groups.filter(name='EC-Signing').exists()
        if is_signing_user and not was_signing_user:
            for u in User.objects.filter(groups__name='EC-Signing'):
                send_system_message_template(u, _('New Signing User'), 'users/new_signing_user.txt', {'user': user})

        messages.success(request, _('The change of the user has been saved.'))

    return render(request, 'users/details.html', {
        'form': form,
    })

@user_group_required('EC-Office', 'EC-Executive Board Member')
def administration(request, limit=20):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'page': '1',
        'groups': [],
        'medical_categories': [],
        'activity': 'active',
        'keyword': '',
    }

    filterdict = request.POST or usersettings.useradministration_filter or filter_defaults
    filterform = AdministrationFilterForm(filterdict)
    if not filterform.is_valid():
        filterform = AdministrationFilterForm(filter_defaults)
        filterform.is_valid()   # force clean

    users = User.objects.distinct()

    if filterform.cleaned_data['activity'] == 'active':
        users = users.filter(is_active=True)
    elif filterform.cleaned_data['activity'] == 'inactive':
        users = users.filter(is_active=False)

    if filterform.cleaned_data['groups']:
        users = users.filter(groups__in=filterform.cleaned_data['groups'])

    if filterform.cleaned_data['medical_categories']:
        users = users.filter(medical_categories__in=filterform.cleaned_data['medical_categories'])

    if filterform.cleaned_data['task_types']:
        users = users.filter(profile__task_uids__overlap=list(
            filterform.cleaned_data['task_types']
                .values_list('workflow_node__uid', flat=True)
        ))

    keyword = filterform.cleaned_data['keyword']
    if keyword:
        keyword_q = Q(username__icontains=keyword) | Q(email__icontains=keyword)
        if ' ' in keyword:
            n1, n2 = keyword.split(' ', 1)
            keyword_q |= Q(first_name__icontains=n1, last_name__icontains=n2)
            keyword_q |= Q(first_name__icontains=n2, last_name__icontains=n1)
        else:
            keyword_q |= Q(first_name__icontains=keyword)
            keyword_q |= Q(last_name__icontains=keyword)
        users = users.filter(keyword_q)

    users = users.select_related('profile').order_by('last_name', 'first_name', 'email')

    paginator = Paginator(users, limit, allow_empty_first_page=True)
    try:
        users = paginator.page(int(filterform.cleaned_data['page']))
    except (EmptyPage, InvalidPage):
        users = paginator.page(1)
        filterform.cleaned_data['page'] = 1

    userfilter = filterform.cleaned_data
    userfilter['groups'] = list(userfilter['groups'].values_list('pk', flat=True))
    userfilter['medical_categories'] = list(userfilter['medical_categories'].values_list('pk', flat=True))
    userfilter['task_types'] = list(userfilter['task_types'].values_list('pk', flat=True))
    usersettings.useradministration_filter = userfilter
    usersettings.save()

    return render(request, 'users/administration.html', {
        'users': users,
        'filterform': filterform,
        'active': 'user_administration',
    })


@user_group_required('EC-Office', 'EC-Executive Board Member')
def invite(request):
    form = InvitationForm(request.POST or None)
    comment = None

    if request.method == 'POST' and form.is_valid():
        user = form.save()

        invitation = Invitation.objects.create(user=user)

        subject = 'Erstellung eines Zugangs zum ECS'
        link = request.build_absolute_uri(
            reverse('ecs.users.views.accept_invitation',
                kwargs={'invitation_uuid': invitation.uuid.hex})
        )
        htmlmail = str(render_html(request, 'users/invitation/invitation_email.html', {
            'invitation_text': form.cleaned_data['invitation_text'],
            'link': link,
        }))
        transferlist = deliver(user.email, subject, None, settings.DEFAULT_FROM_EMAIL, message_html=htmlmail)
        msgid, rawmail = transferlist[0]    # raises IndexError if delivery failed

        if user.groups.filter(name='EC-Signing').exists():
            for u in User.objects.filter(groups__name='EC-Signing'):
                send_system_message_template(u, _('New Signing User'), 'users/new_signing_user.txt', {'user': user})
        return redirect('ecs.users.views.details', user_pk=user.pk)

    return render(request, 'users/invitation/invite_user.html', {
        'form': form,
        'comment': comment,
        'active': 'user_invite',
    })


@forceauth.exempt
def accept_invitation(request, invitation_uuid=None):
    try:
        invitation = Invitation.objects.new().get(uuid=invitation_uuid)
    except Invitation.DoesNotExist:
        raise Http404

    user = invitation.user
    form = SetPasswordForm(invitation.user, request.POST or None)
    if form.is_valid():
        form.save()
        profile = user.profile
        profile.last_password_change = timezone.now()
        profile.is_phantom = False
        profile.forward_messages_after_minutes = 5
        profile.save()
        invitation.is_accepted = True
        invitation.save()
        user = auth.authenticate(email=invitation.user.email, password=form.cleaned_data['new_password1'])
        auth.login(request, user)
        return redirect('ecs.users.views.edit_profile')

    return render(request, 'users/invitation/set_password_form.html', {
        'form': form,
    })

@user_flag_required('is_executive_board_member')
def login_history(request):
    end = timezone.now()
    start = end - timedelta(days=1)
    type = None
    page = 1

    form = LoginHistoryFilterForm(request.POST or None,
        initial={'start': start, 'end': end})
    if request.method == 'POST' and form.is_valid():
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        type = form.cleaned_data.get('type')
        page = form.cleaned_data.get('page')

    events = LoginHistory.objects.filter(
        timestamp__gte=start, timestamp__lte=end).order_by('-timestamp')
    if type:
        events = events.filter(type=type)

    paginator = Paginator(events, 50)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return render(request, 'users/login_history.html', {
        'form': form,
        'page': page,
        'active': 'login_history',
    })
