from django.conf.urls import url

from ecs.tasks import views


urlpatterns = (
    url(r'^list/(?:submission/(?P<submission_pk>\d+)/)?$', views.task_list),
    url(r'^list/mine/(?:submission/(?P<submission_pk>\d+)/)?$', views.my_tasks),
    url(r'^(?P<task_pk>\d+)/accept/$', views.accept_task),
    url(r'^(?P<task_pk>\d+)/accept/full/$', views.accept_task_full),
    url(r'^accept/$', views.accept_tasks),
    url(r'^accept/full/$', views.accept_tasks_full),
    url(r'^(?P<task_pk>\d+)/decline/$', views.decline_task),
    url(r'^(?P<task_pk>\d+)/decline/full/$', views.decline_task_full),
    url(r'^(?P<task_pk>\d+)/do/$', views.do_task),
    url(r'^(?P<task_pk>\d+)/preview/$', views.preview_task),
)
