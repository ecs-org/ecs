from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.users.views',
    url(r'^register/$', 'register'),
    url(r'^activate/(?P<token>.+)$', 'activate'),
    url(r'^profile/$', 'profile'),
    url(r'^profile/change-password/$', 'change_password'),
    url(r'^request-password-reset/$', 'request_password_reset'),
    url(r'^password-reset/(?P<token>.+)$', 'do_password_reset'),
    url(r'^accounts/login/$', 'login'),
    url(r'^accounts/logout/$', 'logout'),
    url(r'^users/(?P<user_pk>\d+)/approve/', 'approve'),
    url(r'^users/pending-approval/$', 'pending_approval_userlist'),
)
