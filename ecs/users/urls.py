from django.conf.urls import url

from ecs.users import views


urlpatterns = (
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/logout/$', views.logout),
    url(r'^accounts/register/$', views.register),

    url(r'^activate/(?P<token>.+)$', views.activate),
    url(r'^profile/$', views.profile),
    url(r'^profile/edit/$', views.edit_profile),
    url(r'^profile/change-password/$', views.change_password),
    url(r'^request-password-reset/$', views.request_password_reset),
    url(r'^password-reset/(?P<token>.+)$', views.do_password_reset),
    url(r'^users/(?P<user_pk>\d+)/indisposition/$', views.indisposition),
    url(r'^users/notify_return/$', views.notify_return),
    url(r'^users/(?P<user_pk>\d+)/toggle_active/$', views.toggle_active),
    url(r'^users/(?P<user_pk>\d+)/details/', views.details),
    url(r'^users/administration/$', views.administration),
    url(r'^users/invite/$', views.invite),
    url(r'^users/login_history/$', views.login_history),
    url(r'^accept_invitation/(?P<invitation_uuid>[\da-zA-Z]{32})/$', views.accept_invitation),
)
