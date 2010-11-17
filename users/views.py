# -*- coding: utf-8 -*-
import time
import datetime
import random

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext as _

from ecs.utils.django_signed import signed
from ecs.utils import forceauth
from ecs.utils.viewutils import render, render_html
from ecs.utils.ratelimitcache import ratelimit_post
from ecs.ecsmail.mail import deliver
from ecs.users.forms import RegistrationForm, ActivationForm, RequestPasswordResetForm, UserForm, ProfileForm, AdministrationFilterForm, \
    UserDetailsForm, ProfileDetailsForm
from ecs.users.models import UserProfile
from ecs.core.models.submissions import attach_to_submissions

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
    return auth_views.login(request, *args, **kwargs)

def logout(request, *args, **kwargs):
    kwargs.setdefault('next_page', '/')
    return auth_views.logout(request, *args, **kwargs)

def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        form.save()
        UserProfile.objects.filter(user=request.user).update(last_password_change=datetime.datetime.now())
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
        deliver(subject=_(u'ECS - Registration'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL, recipient_list=form.cleaned_data['email'])
        return render(request, 'users/registration/registration_complete.html', {})
        
    return render(request, 'users/registration/registration_form.html', {
        'form': form,
    })


@forceauth.exempt
def activate(request, token=None):
    data, timestamp = _registration_token_factory.parse_token_or_404(token)
    try:
        existing_user = User.objects.get(email__iexact=data['email'])
        return render(request, 'users/registration/already_activated.html', {
            'existing_user': existing_user,
        })
    except User.DoesNotExist:
        pass

    form = ActivationForm(request.POST or None)
    if form.is_valid():
        user = User(
            username=form.cleaned_data['username'], 
            first_name=data['first_name'], 
            last_name=data['last_name'],
            email=data['email']
        )
        user.set_password(form.cleaned_data['password'])
        user.save()
        user.groups = Group.objects.filter(name__in=settings.DEFAULT_USER_GROUPS)
        # the userprofile is auto-created, we only have to update some fields.
        UserProfile.objects.filter(user=user).update(gender=data['gender'])
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
        deliver(subject=_(u'ECS - password reset'), message=None, message_html=htmlmail,
            from_email= settings.DEFAULT_FROM_EMAIL, recipient_list=form.cleaned_data['email'])
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
        profile.last_password_change = datetime.datetime.now()
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
    user_form = UserForm(request.POST or None, prefix='user', instance=request.user)
    profile_form = ProfileForm(request.POST or None, prefix='profile', instance=request.user.get_profile())
    
    if profile_form.is_valid() and user_form.is_valid():
        user_form.save()
        profile_form.save()
        return HttpResponseRedirect(reverse('ecs.users.views.profile'))
        
    return render(request, 'users/profile_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


###########################
### User Administration ###
###########################

@user_passes_test(lambda u: u.ecs_profile.internal)
def toggle_indisposed(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.ecs_profile.indisposed:
        user.ecs_profile.indisposed = False
    else:
        user.ecs_profile.indisposed = True

    user.ecs_profile.save()
    return HttpResponseRedirect(reverse('ecs.users.views.administration'))

@user_passes_test(lambda u: u.ecs_profile.internal)
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

@user_passes_test(lambda u: u.ecs_profile.internal)
def toggle_active(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return HttpResponseRedirect(reverse('ecs.users.views.administration'))

@user_passes_test(lambda u: u.ecs_profile.internal)
def details(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    user_form = UserDetailsForm(request.POST or None, instance=user, prefix='user')
    profile_form = ProfileDetailsForm(request.POST or None, instance=user.ecs_profile, prefix='profile')
    if request.method == 'POST':
        if user_form.is_valid():
            user_form.save()
            user_form.save_m2m()
        if profile_form.is_valid():
            profile_form.save()
            profile_form.save_m2m()

    return render(request, 'users/details.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@user_passes_test(lambda u: u.ecs_profile.internal)
def administration(request):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'group': '',
        'approval': 'both',
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

    if filterform.cleaned_data['group']:
        users = users.filter(groups=filterform.cleaned_data['group'])

    print filterform.cleaned_data['group']

    return render(request, 'users/administration.html', {
        'users': users.order_by('username'),
        'filterform': filterform,
        'form_id': 'useradministration_filter_%s' % random.randint(1000000, 9999999),
    })

