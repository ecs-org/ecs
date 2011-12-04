from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^popup/$', 'ecs.feedback.views.feedback_input'),
    url(r'^(?P<type>[a-z])/$', 'ecs.feedback.views.feedback_input'),
    url(r'^(?P<type>[a-z])/(?P<page>\d+)/$', 'ecs.feedback.views.feedback_input'),
    url(r'^(?P<type>[a-z])/(?P<page>\d+)/(?P<origin>[^/]+)/$', 'ecs.feedback.views.feedback_input', name='feedback_input'),
)
