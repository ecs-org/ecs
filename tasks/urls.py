from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.tasks.views',
    url(r'^mine/', 'my_tasks'),
    url(r'^backlog/', 'task_backlog'),
    url(r'^task/(?P<task_pk>\d+)/done/', 'do_task'),
    url(r'^task/(?P<task_pk>\d+)/accept/', 'accept_task'),
    url(r'^task/(?P<task_pk>\d+)/decline/', 'decline_task'),
    url(r'^task/(?P<task_pk>\d+)/manage/', 'manage_task'),
)

