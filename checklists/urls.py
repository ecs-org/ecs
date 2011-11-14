from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.checklists.views',
    url(r'^comments/(?P<checklist_pk>\d+)/(?P<flavour>positive|negative)/', 'checklist_comments'),
    url(r'^pdf/(?P<checklist_pk>\d+)/$', 'checklist_pdf'),
)
