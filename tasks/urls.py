from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.tasks.views',
    url(r'^mine/', 'my_tasks'),
    url(r'^backlog/', 'task_backlog'),
)

