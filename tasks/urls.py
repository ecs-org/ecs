from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.tasks.views',
    url(r'^mine/$', 'my_tasks'),
    url(r'^mine/submission/(?P<submission_pk>\d+)/$', 'my_tasks'),
    url(r'^list/$', 'task_list'),
    url(r'^list/submission/(?P<submission_pk>\d+)/$', 'task_list'),
    url(r'^backlog/$', 'task_backlog', {'template': 'tasks/backlog.html'}),
    url(r'^task/(?P<task_pk>\d+)/accept/$', 'accept_task'),
    url(r'^task/(?P<task_pk>\d+)/accept/full/$', 'accept_task_full'),
    url(r'^task/(?P<task_pk>\d+)/decline/$', 'decline_task'),
    url(r'^task/(?P<task_pk>\d+)/decline/full/$', 'decline_task_full'),
    url(r'^task/(?P<task_pk>\d+)/manage/$', 'manage_task'),
    url(r'^task/(?P<task_pk>\d+)/reopen/$', 'reopen_task'),
)

