from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    url(r'^$', 'ecs.core.views.index'),

    url(r'^notification/new/$', 'ecs.core.views.select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'ecs.core.views.view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'ecs.core.views.notification_pdf'),
    url(r'^notification/(?P<notification_pk>\d+)/xhtml2pdf/$', 'ecs.core.views.notification_xhtml2pdf'),
    url(r'^notifications/$', 'ecs.core.views.notification_list'),
    url(r'^submission_data_for_notification/$', 'ecs.core.views.submission_data_for_notification'),

    url(r'^document/(?P<document_pk>\d+)/download/$', 'ecs.core.views.download_document'),

    url(r'^submission_form/(?P<submission_form_pk>\d+)/$', 'ecs.core.views.view_submission_form'),
    url(r'^submission_form/new/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_submission_form'),
    url(r'^submission_forms/$', 'ecs.core.views.submission_form_list'),
)
