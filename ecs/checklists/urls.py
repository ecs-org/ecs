from django.conf.urls import *

urlpatterns = patterns('ecs.checklists.views',
    url(r'^(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', 'checklist_comments'),
)
