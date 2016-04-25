import json

from django.conf.urls import url
from django.http import HttpResponse
from ecs.docstash.decorators import with_docstash


@with_docstash()
def simple_post_view(request):
    if request.method == 'POST':
        request.docstash.value = request.POST.dict()
        request.docstash.save()
    return HttpResponse(json.dumps(request.docstash.value), content_type='text/json')

urlpatterns = (
    url(r'^simple_post/(?:(?P<docstash_key>.*)/)?$', simple_post_view),
)
