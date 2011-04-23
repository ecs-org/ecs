# -*- coding: utf-8 -*-
import time
from datetime import datetime
import random
from uuid import uuid4

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
from django.contrib import auth
from django.db.models import Q

from ecs.utils.django_signed import signed
from ecs.utils import forceauth
from ecs.utils.viewutils import render, render_html
from ecs.utils.ratelimitcache import ratelimit_post
from ecs.ecsmail.mail import deliver
from ecs.users.forms import RegistrationForm, ActivationForm, RequestPasswordResetForm, ProfileForm, AdministrationFilterForm, \
    UserDetailsForm, ProfileDetailsForm, InvitationForm
from ecs.users.models import UserProfile, Invitation
from ecs.core.models.submissions import attach_to_submissions
from ecs.users.utils import user_flag_required, invite_user
from ecs.users.forms import EmailLoginForm
from ecs.users.utils import get_user, create_user
from ecs.workflow.models import Graph


class TimestampedTokenFactory(object):
    def __init__(self, extra_key=None, ttl=3600):
        self.extra_key = extra_key
        self.ttl = ttl
        
    def generate_token(self, data):
        return signed.dumps((data, time.time()), extra_key=self.extra_key)
        
    def parse_token(self, token):
        data, timestamp = signed.loads(token, extra_key=self.extra_key)
        if time.time() - timestamp > self.ttl:
            raise ValueError("token expired")
        return data, timestamp
        
    def parse_token_or_404(self, token):
        try:
            return self.parse_token(token)
        except ValueError, e:
            raise Http404(e)
        
_password_reset_token_factory = TimestampedTokenFactory(extra_key=settings.REGISTRATION_SECRET)
_registration_token_factory = TimestampedTokenFactory(extra_key=settings.PASSWORD_RESET_SECRET)

@forceauth.exempt
@ratelimit_post(minutes=5, requests=5, key_field='username')
def login(request, *args, **kwargs):
    kwargs.setdefault('template_name', 'users/login.html')
    kwargs['authentication_form'] = EmailLoginForm
    return auth_views.login(request, *args, **kwargs)

def logout(request, *args, **kwargs):
    kwargs.setdefault('next_page', '/')
    return auth_views.logout(request, *args, **kwargs)

def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        UserProfile.objects.filter(user=request.user).update(last_password_change=datetime.now())
        return render(request, 'users/change_password_complete.html', {})
    return render(request, 'users/change_password_form.html', {
        'form': form,
    })


@forceauth.exempt
@ratelimit_post(minutes=5, requests=5, key_field='email')
def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        token = _registration_token_factory.generate_token(form.cleaned_data)
        activation_url = request.build_absolute_uri(reverse('ecs.users.views.activate', kwargs={'token': token}))        
        htmlmail = unicode(render_html(request, 'users/registration/activation_email.html', {
            'activation_url': activation_url,
            'form': form,
        }))
        deliver(form.cleaned_data['email'], subject=_(u'ECS - Registration'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL)
        return render(request, 'users/registration/registration_complete.html', {})
        
    return render(request, 'users/registration/registration_form.html', {
        'form': form,
    })


@forceauth.exempt
def activate(request, token=None):
    data, timestamp = _registration_token_factory.parse_token_or_404(token)
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
        user.groups = Group.objects.filter(name__in=settings.DEFAULT_USER_GROUPS)
        # the userprofile is auto-created, we only have to update some fields.
        user.ecs_profile.gender = data['gender']
        user.ecs_profile.forward_messages_after_minutes = 5
        user.ecs_profile.save()

        wf = Graph.objects.get(model=UserProfile, auto_start=True).create_workflow(data=user.ecs_profile)
        wf.start()

        return render(request, 'users/registration/activation_complete.html', {
            'activated_user': user,
        })
        
    return render(request, 'users/registration/activation_form.html', {
        'form': form,
        'data': data,
    })


@forceauth.exempt
@ratelimit_post(minutes=5, requests=5, key_field='email')
def request_password_reset(request):
    form = RequestPasswordResetForm(request.POST or None)
    if form.is_valid():
        token = _password_reset_token_factory.generate_token(form.cleaned_data['email'])
        reset_url = request.build_absolute_uri(reverse('ecs.users.views.do_password_reset', kwargs={'token': token}))
        htmlmail = unicode(render_html(request, 'users/password_reset/reset_email.html', {
            'reset_url': reset_url,
        }))
        deliver(form.cleaned_data['email'], subject=_(u'ECS - Password Reset'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL)
        return render(request, 'users/password_reset/request_complete.html', {
            'email': form.cleaned_data['email'],
        })
    return render(request, 'users/password_reset/request_form.html', {
        'form': form,
    })


@forceauth.exempt
def do_password_reset(request, token=None):
    email, timestamp = _password_reset_token_factory.parse_token_or_404(token)
    user = get_object_or_404(User, email=email)
    profile = user.get_profile()
    if profile.last_password_change and time.mktime(profile.last_password_change.timetuple()) > timestamp:
        return render(request, 'users/password_reset/token_already_used.html', {})
    
    form = SetPasswordForm(user, request.POST or None)
    if form.is_valid():
        form.save()
        profile.last_password_change = datetime.now()
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
    form = ProfileForm(request.POST or None, instance=request.user.get_profile())
    
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('ecs.users.views.profile'))
        
    return render(request, 'users/profile_form.html', {
        'form': form,
    })


###########################
### User Administration ###
###########################

@user_flag_required('internal')
def toggle_indisposed(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.ecs_profile.indisposed:
        user.ecs_profile.indisposed = False
    else:
        user.ecs_profile.indisposed = True

    user.ecs_profile.save()
    return HttpResponseRedirect(reverse('ecs.users.views.administration'))

@user_flag_required('internal')
def approve(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if request.method == 'POST':
        approved = request.POST.get('approve', False)
        UserProfile.objects.filter(user=user).update(approved_by_office=approved)
        if approved:
            attach_to_submissions(user)
    return render(request, 'users/approve.html', {
        'profile_user': user,
    })

@user_flag_required('internal')
def toggle_active(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return HttpResponseRedirect(reverse('ecs.users.views.administration'))

@user_flag_required('internal')
def details(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    user_form = UserDetailsForm(request.POST or None, instance=user, prefix='user')
    profile_form = ProfileDetailsForm(request.POST or None, instance=user.ecs_profile, prefix='profile')
    if request.method == 'POST':
        if user_form.is_valid():
            user_form.save()
        if profile_form.is_valid():
            profile_form.save()

    return render(request, 'users/details.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@user_flag_required('internal')
def administration(request, limit=20):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'page': '1',
        'group': '',
        'approval': 'both',
        'activity': 'active',
        'keyword': '',
    }

    filterdict = request.POST or usersettings.useradministration_filter or filter_defaults
    filterform = AdministrationFilterForm(filterdict)
    filterform.is_valid()  # force clean

    approval_lookup = {
        'both': User.objects.all(),
        'yes': User.objects.filter(ecs_profile__approved_by_office=True),
        'no': User.objects.filter(ecs_profile__approved_by_office=False),
    }

    users = approval_lookup[filterform.cleaned_data['approval']]

    if filterform.cleaned_data['activity'] == 'active':
        users = users.filter(is_active=True)
    elif filterform.cleaned_data['activity'] == 'inactive':
        users = users.filter(is_active=False)

    if filterform.cleaned_data['group']:
        users = users.filter(groups=filterform.cleaned_data['group'])

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


    paginator = Paginator(users.order_by('last_name', 'first_name', 'email'), limit, allow_empty_first_page=True)
    try:
        users = paginator.page(int(filterform.cleaned_data['page']))
    except EmptyPage, InvalidPage:
        users = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = AdministrationFilterForm(filterform.cleaned_data)
        filterform.is_valid()

    userfilter = filterform.cleaned_data
    userfilter['group'] = userfilter['group'].pk if userfilter['group'] else ''
    usersettings.useradministration_filter = userfilter
    usersettings.save()

    return render(request, 'users/administration.html', {
        'users': users,
        'filterform': filterform,
        'form_id': 'useradministration_filter_%s' % random.randint(1000000, 9999999),
    })

@user_flag_required('internal')
def invite(request):
    form = InvitationForm(request.POST or None)
    comment = invite_user(request, form.cleaned_data['email']) if form.is_valid() else None

    return render(request, 'users/invitation/invite_user.html', {
        'form': form,
        'comment': comment,
    })


@forceauth.exempt
def accept_invitation(request, invitation_uuid=None):
    try:
        invitation = Invitation.objects.new().get(uuid=invitation_uuid.lower())
    except Invitation.DoesNotExist:
        raise Http404

    form = PasswordChangeForm(invitation.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        user.ecs_profile.last_password_change = datetime.now()
        user.ecs_profile.phantom = False
        user.ecs_profile.save()
        invitation.accepted = True
        invitation.save()
        user = auth.authenticate(email=invitation.user.email, password=form.cleaned_data['new_password1'])
        auth.login(request, user)
        return HttpResponseRedirect(reverse('ecs.users.views.edit_profile'))

    password = uuid4().get_hex()
    invitation.user.set_password(password)
    invitation.user.save()
    form.fields['old_password'].widget = forms.HiddenInput()
    form.fields['old_password'].initial = password

    return render(request, 'users/invitation/set_password_form.html', {
        'form': form,
    })

