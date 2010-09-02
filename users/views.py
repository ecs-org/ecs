import time
import datetime

from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import views as auth_views
from django.conf import settings

from ecs.utils.django_signed import signed
from ecs.utils import forceauth
from ecs.core.views.utils import render, render_html
from ecs.ecsmail.mail import send_html_email
from ecs.users.forms import RegistrationForm, ActivationForm, RequestPasswordResetForm
from ecs.users.models import UserProfile


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
        return data
        
    def parse_token_or_404(self, token):
        try:
            return self.parse_token(token)
        except ValueError, e:
            raise Http404(e)
        
_password_reset_token_factory = TimestampedTokenFactory(extra_key=settings.REGISTRATION_SECRET)
_registration_token_factory = TimestampedTokenFactory(extra_key=settings.PASSWORD_RESET_SECRET)

@forceauth.exempt
def login(request, *args, **kwargs):
    kwargs.setdefault('template_name', 'users/login.html')
    return auth_views.login(request, *args, **kwargs)

def logout(request, *args, **kwargs):
    kwargs.setdefault('next_page', '/')
    return auth_views.logout(request, *args, **kwargs)


def profile(request):
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
    })


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
def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        token = _registration_token_factory.generate_token(form.cleaned_data)
        activation_url = request.build_absolute_uri(reverse('ecs.users.views.activate', kwargs={'token': token}))        
        htmlmail = unicode(render_html(request, 'users/registration/activation_email.html', {
            'activation_url': activation_url,
            'form': form,
        }))
        # FIXME: this should go into a celery queue and not be called directly
        send_html_email(subject='ECS - Anmeldung', message_html=htmlmail, recipient_list=form.cleaned_data['email'])
        return render(request, 'users/registration/registration_complete.html', {})
        
    return render(request, 'users/registration/registration_form.html', {
        'form': form,
    })


@forceauth.exempt
def activate(request, token=None):
    data = _registration_token_factory.parse_token_or_404(token)
    try:
        existing_user = User.objects.get(email=data['email'])
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
def request_password_reset(request):
    form = RequestPasswordResetForm(request.POST or None)
    if form.is_valid():
        token = _password_reset_token_factory.generate_token(form.cleaned_data['email'])
        reset_url = request.build_absolute_uri(reverse('ecs.users.views.do_password_reset', kwargs={'token': token}))
        htmlmail = unicode(render_html(request, 'users/password_reset/reset_email.html', {
            'reset_url': reset_url,
        }))
        send_html_email(subject='ECS - Passwort vergessen', message_html=htmlmail, recipient_list=form.cleaned_data['email'])
        return render(request, 'users/password_reset/request_complete.html', {
            'email': form.cleaned_data['email'],
        })
    return render(request, 'users/password_reset/request_form.html', {
        'form': form,
    })


@forceauth.exempt
def do_password_reset(request, token=None):
    email = _password_reset_token_factory.parse_token_or_404(token)
    user = get_object_or_404(User, email=email)
    form = SetPasswordForm(user, request.POST or None)
    if form.is_valid():
        form.save()
        UserProfile.objects.filter(user=user).update(last_password_change=datetime.datetime.now())
        return render(request, 'users/password_reset/reset_complete.html', {})
    return render(request, 'users/password_reset/reset_form.html', {
        'user': user,
        'form': form,
    })
    
def pending_approval_userlist(request):
    return render(request, 'users/pending_approval_list.html', {
        'users': User.objects.filter(ecs_profile__approved_by_office=False),
    })
    
def approve(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if request.method == 'POST':
        print request.POST
        UserProfile.objects.filter(user=user).update(approved_by_office=request.POST.get('approve', False))
    return render(request, 'users/approve.html', {
        'profile_user': user,
    })
            