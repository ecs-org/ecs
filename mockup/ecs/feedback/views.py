"""
Feedback Views
==============

Since this is a generic view for ajax callbacks, it expects to have the model
passed in as an argument.  The model can either be an actual model class, or a
string that is looked up in settings.FEEDBACK_MODELS
"""

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.conf import settings
from django import http

from ecs.feedback.models import FeedbackComment
from ecs.feedback.utils import lookup_model

def feedback_summary(request, modelstr=None, id=None):
    """
    For a given model and id, return the feedback summary list

    The model argument can either be a class object or a string that
    can be resolved to a class object in settings.FEEDBACK_MODELS
    """
    model = lookup_model(modelstr)
    if not model:
        raise http.Http404
    object = model.objects.get(pk=id)
    if not object:
        raise http.Http404
    ctype = ContentType.objects.get_for_model(model)
    comments = FeedbackComment.objects.filter(
        content_type__pk=ctype.id,
        object_id=id).order_by('submit_date').all()
    return render_to_response("feedback/feedbacksummary.html", {
        "object" : object,
        "comment_list" : comments,
    })


def feedback_form(request, modelstr=None, id=None):
    """
    For a given model and id, return the Ajax comment form
    """
    model = lookup_model(modelstr)
    if not model:
        raise http.Http404
    object = model.objects.get(pk=id)
    if not object:
        raise http.Http404
    return render_to_response("feedback/feedbackform.html", {
        "comment_object" : object,
        "modelstr": modelstr,
        "objectid" : id,
    })
