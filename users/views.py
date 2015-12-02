# -*- coding: utf-8 -*-
import time
from datetime import datetime
import random

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import auth
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.views.decorators.http import require_POST

from ecs.utils.django_signed import signed
from ecs.utils import forceauth
from ecs.utils.viewutils import render, render_html
from ecs.utils.ratelimitcache import ratelimit_post
from ecs.utils.security import readonly
from ecs.ecsmail.utils import deliver
from ecs.users.forms import RegistrationForm, ActivationForm, RequestPasswordResetForm, ProfileForm, AdministrationFilterForm, \
    UserDetailsForm, InvitationForm
from ecs.users.models import UserProfile, Invitation, LoginHistory
from ecs.users.forms import EmailLoginForm, IndispositionForm, SetPasswordForm, PasswordChangeForm
from ecs.users.utils import get_user, create_user, user_group_required
from ecs.communication.utils import send_system_message_template
from ecs.utils.browserutils import UA
from ecs.help.models import Page


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
        
_password_reset_token_factory = TimestampedTokenFactory(extra_key=settings.REGISTRATION_SECRET)
_registration_token_factory = TimestampedTokenFactory(extra_key=settings.PASSWORD_RESET_SECRET, ttl=86400)

@forceauth.exempt
@ratelimit_post(minutes=5, requests=15, key_field='username')
def login(request, *args, **kwargs):
    if request.is_ajax():
        return HttpResponse('<script type="text/javascript">window.location.href="%s";</script>' % reverse('ecs.users.views.login'))

    ua_str = request.META.get('HTTP_USER_AGENT')
    if ua_str:
        request.ua = UA(ua_str)
        if request.ua.is_unsupported:
            try:
                page = Page.objects.get(slug='html5')
                url = reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk})
            except Page.DoesNotExist:
                url = reverse('ecs.help.views.index')
            return HttpResponseRedirect(url)
        elif request.ua.is_tmp_unsupported:
            return render(request, 'browser_temporarily_unsupported.html', {})

    kwargs.setdefault('template_name', 'users/login.html')
    kwargs['authentication_form'] = EmailLoginForm
    response = auth_views.login(request, *args, **kwargs)
    if request.user.is_authenticated():
        LoginHistory.objects.create(type='login', user=request.user)
    return response


@readonly()
def logout(request, *args, **kwargs):
    kwargs.setdefault('next_page', '/')
    user = getattr(request, 'original_user', request.user)
    response = auth_views.logout(request, *args, **kwargs)
    if not request.user.is_authenticated():
        LoginHistory.objects.create(type='logout', user=user)
    return response


@readonly(methods=['GET'])
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
@ratelimit_post(minutes=5, requests=15, key_field='email')
@readonly(methods=['GET'])
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
            from_email= settings.DEFAULT_FROM_EMAIL, nofilter=True)
        return render(request, 'users/registration/registration_complete.html', {})
        
    return render(request, 'users/registration/registration_form.html', {
        'form': form,
    })


@forceauth.exempt
@readonly(methods=['GET'])
def activate(request, token=None):
    try:
        data, timestamp = _registration_token_factory.parse_token(token)
    except ValueError, e:
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
        profile = user.get_profile()
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
@readonly(methods=['GET'])
def request_password_reset(request):
    form = RequestPasswordResetForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        if email != 'root@system.local':
            try:
                user = get_user(email)
            except User.DoesNotExist:
                register_url = request.build_absolute_uri(reverse('ecs.users.views.register'))
                htmlmail = unicode(render_html(request, 'users/password_reset/register_email.html', {
                    'register_url': register_url,
                    'email': email,
                }))
            else:
                token = _password_reset_token_factory.generate_token(email)
                reset_url = request.build_absolute_uri(reverse('ecs.users.views.do_password_reset', kwargs={'token': token}))
                htmlmail = unicode(render_html(request, 'users/password_reset/reset_email.html', {
                    'reset_url': reset_url,
                }))
            deliver(email, subject=_(u'ECS - Password Reset'), message=None, message_html=htmlmail,
                from_email= settings.DEFAULT_FROM_EMAIL, nofilter=True)
        return render(request, 'users/password_reset/request_complete.html', {
            'email': email,
        })
    return render(request, 'users/password_reset/request_form.html', {
        'form': form,
    })


@forceauth.exempt
@readonly(methods=['GET'])
def do_password_reset(request, token=None):
    try:
        email, timestamp = _password_reset_token_factory.parse_token(token)
    except ValueError, e:
        return render(request, 'users/password_reset/reset_token_invalid.html', {})

    try:
        user = get_user(email)
    except User.DoesNotExist:
        raise Http404()
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


@readonly()
def profile(request):
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
    })

@readonly(methods=['GET'])
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

def notify_return(request):
    profile = request.user.get_profile()
    profile.is_indisposed = False
    profile.save()
    return HttpResponseRedirect(reverse('ecs.users.views.profile'))


@readonly(methods=['GET'])
@user_group_required('EC-Office', 'EC-Executive Board Group')
def indisposition(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    form = IndispositionForm(request.POST or None, instance=user.get_profile())

    if request.method == 'POST' and form.is_valid():
        form.save()
        profile = user.get_profile()
        if profile.is_indisposed:
            send_system_message_template(profile.communication_proxy, _('{user} indisposed').format(user=user), 'users/indisposed_proxy.txt', {'user': user})
        return HttpResponseRedirect(reverse('ecs.users.views.administration'))

    return render(request, 'users/indisposition.html', {
        'profile_user': user,
        'form': form,
    })


@require_POST
@user_group_required('EC-Office', 'EC-Executive Board Group')
def toggle_active(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return HttpResponseRedirect(reverse('ecs.users.views.administration'))


@readonly(methods=['GET'])
@user_group_required('EC-Office', 'EC-Executive Board Group')
def details(request, user_pk=None):
    user = get_object_or_404(User, pk=user_pk)
    was_signing_user = user.groups.filter(name=u'EC-Signing Group').exists()
    form = UserDetailsForm(request.POST or None, instance=user, prefix='user')
    saved = False
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        saved = True
        is_signing_user = user.groups.filter(name=u'EC-Signing Group').exists()
        if is_signing_user and not was_signing_user:
            for u in User.objects.filter(groups__name=u'EC-Signing Group'):
                send_system_message_template(u, _('New Signing User'), 'users/new_signing_user.txt', {'user': user})

    return render(request, 'users/details.html', {
        'form': form,
        'saved': saved,
    })

@user_group_required('EC-Office', 'EC-Executive Board Group')
def administration(request, limit=20):
    usersettings = request.user.ecs_settings

    filter_defaults = {
        'page': '1',
        'groups': '',
        'medical_categories': '',
        'activity': 'active',
        'keyword': '',
    }

    filterdict = request.POST or usersettings.useradministration_filter or filter_defaults
    filterform = AdministrationFilterForm(filterdict)
    filterform.is_valid()  # force clean

    users = User.objects.all()

    if filterform.cleaned_data['activity'] == 'active':
        users = users.filter(is_active=True)
    elif filterform.cleaned_data['activity'] == 'inactive':
        users = users.filter(is_active=False)

    if filterform.cleaned_data['groups']:
        users = users.filter(groups__in=filterform.cleaned_data['groups'])

    if filterform.cleaned_data['medical_categories']:
        users = users.filter(medical_categories__in=filterform.cleaned_data['medical_categories'])

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

    users = users.select_related('ecs_profile').order_by('last_name', 'first_name', 'email')

    paginator = Paginator(users, limit, allow_empty_first_page=True)
    try:
        users = paginator.page(int(filterform.cleaned_data['page']))
    except EmptyPage, InvalidPage:
        users = paginator.page(1)
        filterform.cleaned_data['page'] = 1
        filterform = AdministrationFilterForm(filterform.cleaned_data)
        filterform.is_valid()

    userfilter = filterform.cleaned_data
    userfilter['groups'] = ','.join([str(g.pk) for g in userfilter['groups']]) if userfilter['groups'] else ''
    userfilter['medical_categories'] = ','.join([str(g.pk) for g in userfilter['medical_categories']]) if userfilter['medical_categories'] else ''
    usersettings.useradministration_filter = userfilter
    usersettings.save()

    return render(request, 'users/administration.html', {
        'users': users,
        'filterform': filterform,
        'form_id': 'useradministration_filter_%s' % random.randint(1000000, 9999999),
        'active': 'user_administration',
    })


@readonly(methods=['GET'])
@user_group_required('EC-Office', 'EC-Executive Board Group')
def invite(request):
    form = InvitationForm(request.POST or None)
    comment = None

    if request.method == 'POST' and form.is_valid():
        from django.db import transaction
        sid = transaction.savepoint()
        try:
            user = form.save()

            invitation = Invitation.objects.create(user=user)

            subject = 'Erstellung eines Zugangs zum ECS'
            link = request.build_absolute_uri(reverse('ecs.users.views.accept_invitation', kwargs={'invitation_uuid': invitation.uuid}))
            htmlmail = unicode(render_html(request, 'users/invitation/invitation_email.html', {
                'invitation_text': form.cleaned_data['invitation_text'],
                'link': link,
            }))
            transferlist = deliver(user.email, subject, None, settings.DEFAULT_FROM_EMAIL, message_html=htmlmail)
            msgid, rawmail = transferlist[0]    # raises IndexError if delivery failed
        except IndexError, e:
            transaction.savepoint_rollback(sid)
            form._errors['email'] = form.error_class([_('Failed to deliver invitation')])
        except:
            transaction.savepoint_rollback(sid)
            raise
        else:
            transaction.savepoint_commit(sid)
            if user.groups.filter(name=u'EC-Signing Group').exists():
                for u in User.objects.filter(groups__name=u'EC-Signing Group'):
                    send_system_message_template(u, _('New Signing User'), 'users/new_signing_user.txt', {'user': user})
            return HttpResponseRedirect(reverse('ecs.users.views.details', kwargs={'user_pk': user.pk}))

    return render(request, 'users/invitation/invite_user.html', {
        'form': form,
        'comment': comment,
        'active': 'user_invite',
    })


@forceauth.exempt
def accept_invitation(request, invitation_uuid=None):
    try:
        invitation = Invitation.objects.new().get(uuid=invitation_uuid.lower())
    except Invitation.DoesNotExist:
        raise Http404

    user = invitation.user
    form = SetPasswordForm(invitation.user, request.POST or None)
    if form.is_valid():
        form.save()
        profile = user.get_profile()
        profile.last_password_change = datetime.now()
        profile.is_phantom = False
        profile.forward_messages_after_minutes = 5
        profile.save()
        invitation.is_accepted = True
        invitation.save()
        user = auth.authenticate(email=invitation.user.email, password=form.cleaned_data['new_password1'])
        auth.login(request, user)
        return HttpResponseRedirect(reverse('ecs.users.views.edit_profile'))

    return render(request, 'users/invitation/set_password_form.html', {
        'form': form,
    })

