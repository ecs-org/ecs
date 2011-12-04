from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.checklists.views',
    url(r'^(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', 'checklist_comments'),
    url(r'^(?P<checklist_pk>\d+)/pdf/$', 'checklist_pdf'),
)
