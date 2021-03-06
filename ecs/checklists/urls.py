from django.conf import settings
from django.conf.urls import url

from ecs.checklists import views


urlpatterns = (
    url(r'^(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', views.checklist_comments),
    url(r'^(?P<checklist_pk>\d+)/pdf/$', views.checklist_pdf),
    url(r'^create_task/submission/(?P<submission_pk>\d+)/$', views.create_task),
    url(r'^categorization_tasks/submissions/(?P<submission_pk>\d+)/$', views.categorization_tasks),
)

if settings.DEBUG:
    urlpatterns += (
        url(r'^(?P<checklist_pk>\d+)/pdf/debug/$', views.checklist_pdf_debug),
    )
