from django.conf.urls import url

from ecs.help import views


urlpatterns = (
    url(r'^$', views.index),
    url(r'^search/$', views.search),
    
    url(r'^page/new/$', views.edit_help_page),
    url(r'^page/(?P<page_pk>\d+)/$', views.view_help_page),
    url(r'^page/(?P<page_pk>\d+)/delete/$', views.delete_help_page),
    url(r'^page/(?P<page_pk>\d+)/edit/$', views.edit_help_page),

    url(r'^page/(?P<page_pk>\d+)/ready_for_review/$', views.ready_for_review),
    url(r'^page/(?P<page_pk>\d+)/review_ok/$', views.review_ok),
    url(r'^page/(?P<page_pk>\d+)/review_fail/$', views.review_fail),
    
    url(r'^view/(?P<view_pk>\d+)/(?:(?P<anchor>[\w-]+)/)?$', views.find_help),
    url(r'^edit/view/(?P<view_pk>\d+)/(?:(?P<anchor>[\w-]+)/)?$', views.edit_help_page),

    url(r'^diff/(?P<page_pk>\d+)/$', views.difference_help_pages),

    url(r'^preview/$', views.preview_help_page_text),
    url(r'^attachments/$', views.attachments),
    url(r'^attachments/upload/$', views.upload),
    url(r'^attachments/find/$', views.find_attachments),
    url(r'^attachments/(?P<attachment_pk>\d+)/delete/$', views.delete_attachment),
    url(r'^attachment/(?P<attachment_pk>\d+)/download/$', views.download_attachment),
    
    url(r'^screenshot/$', views.screenshot),

    url(r'^export/$', views.export),
    url(r'^import/$', views.load),
    url(r'^review/$', views.review_overview),
)
