from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.tasks.views',
    url(r'^mine/$', 'my_tasks'),
    url(r'^list/$', 'list'),
    url(r'^popup/$', 'popup'),
    url(r'^backlog/$', 'task_backlog', {'template': 'tasks/backlog.html'}),
    url(r'^task/(?P<task_pk>\d+)/accept/$', 'accept_task'),
    url(r'^task/(?P<task_pk>\d+)/decline/$', 'decline_task'),
    url(r'^task/(?P<task_pk>\d+)/manage/$', 'manage_task'),
    url(r'^task/(?P<task_pk>\d+)/reopen/$', 'reopen_task'),
)

