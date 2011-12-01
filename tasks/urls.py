from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.tasks.views',
    url(r'^list/$', 'task_list'),
    url(r'^list/submission/(?P<submission_pk>\d+)/$', 'task_list'),
    url(r'^list/mine/$', 'my_tasks'),
    url(r'^list/mine/submission/(?P<submission_pk>\d+)/$', 'my_tasks'),
    url(r'^backlog/$', 'task_backlog', {'template': 'tasks/backlog.html'}),

    url(r'^(?P<task_pk>\d+)/accept/$', 'accept_task'),
    url(r'^(?P<task_pk>\d+)/accept/full/$', 'accept_task_full'),
    url(r'^(?P<task_pk>\d+)/decline/$', 'decline_task'),
    url(r'^(?P<task_pk>\d+)/decline/full/$', 'decline_task_full'),
    url(r'^(?P<task_pk>\d+)/reopen/$', 'reopen_task'),
)

