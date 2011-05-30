from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.users.views',
    url(r'^register/$', 'register'),
    url(r'^activate/(?P<token>.+)$', 'activate'),
    url(r'^profile/$', 'profile'),
    url(r'^profile/edit/$', 'edit_profile'),
    url(r'^profile/change-password/$', 'change_password'),
    url(r'^request-password-reset/$', 'request_password_reset'),
    url(r'^password-reset/(?P<token>.+)$', 'do_password_reset'),
    url(r'^accounts/login/$', 'login'),
    url(r'^accounts/logout/$', 'logout'),
    url(r'^users/(?P<user_pk>\d+)/approve/', 'approve'),
    url(r'^users/(?P<user_pk>\d+)/toggle_indisposed/$', 'toggle_indisposed'),
    url(r'^users/notify_return/$', 'notify_return'),
    url(r'^users/(?P<user_pk>\d+)/toggle_active/$', 'toggle_active'),
    url(r'^users/(?P<user_pk>\d+)/details/', 'details'),
    url(r'^administration/$', 'administration'),
    url(r'^invite/$', 'invite'),
    url(r'^accept_invitation/(?P<invitation_uuid>[\da-zA-Z]{32})/$', 'accept_invitation'),
)

