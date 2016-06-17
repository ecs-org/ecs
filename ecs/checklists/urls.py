from django.conf.urls import url

from ecs.checklists import views


urlpatterns = (
    url(r'^(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', views.checklist_comments),
    url(r'^(?P<checklist_pk>\d+)/pdf/$', views.checklist_pdf),
    url(r'^create_task/submission/(?P<submission_pk>\d+)/$', views.create_task),
)
