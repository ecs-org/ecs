from django.conf.urls import url

from ecs.communication import views


urlpatterns = (
    url(r'^list/(?:(?P<submission_pk>\d+)/)?$', views.list_threads),
    url(r'^widget/$', views.dashboard_widget),
    url(r'^widget/overview/(?P<submission_pk>\d+)/$', views.communication_overview_widget),
    url(r'^new/(?:(?P<submission_pk>\d+)/)?(?:(?P<to_user_pk>\d+)/)?$', views.new_thread),
    url(r'^(?P<thread_pk>\d+)/read/$', views.read_thread),
    url(r'^(?P<thread_pk>\d+)/mark_read/$', views.mark_read),
    url(r'^(?P<thread_pk>\d+)/star/$', views.star),
    url(r'^(?P<thread_pk>\d+)/unstar/$', views.unstar),
)
