from django.shortcuts import render_to_response, get_object_or_404

from ecs.mockup.models import Mockup

def mockup(request, id):
    object = get_object_or_404(Mockup, pk=id)
    return render_to_response("mockup/mockup.html", {
        "mockup" : object,
    })
