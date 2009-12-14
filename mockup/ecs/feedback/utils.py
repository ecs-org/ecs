from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template
from django.conf import settings
from django import http

def lookup_model(model):
    """
    For a model string or class object, return the model class
    with the provided primary key.
    """
    # FIXME: we cannot import models directly in settings,
    # so we should contain a modulename:class mapping in
    # settings.FEEDBACK_MODELS, and we should look that up
    # here
    if isinstance(model, basestring):
        models = getattr(settings, 'FEEDBACK_MODELS', {})
        model = models.get(model, None)
    return model

def new_comment(request):
    if request.method != 'POST':
        return

